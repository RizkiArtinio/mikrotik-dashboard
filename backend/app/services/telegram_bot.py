"""Inbound Telegram bot: lets whitelisted chat IDs generate VPN accounts
(L2TP/IPsec, OpenVPN) and list existing ones via chat commands. Separate
from notifiers/telegram_notifier.py, which only sends outbound alerts —
this module also polls Telegram for incoming messages.
"""

import asyncio
import html
import logging
import re

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.router import Router
from app.models.vpn_peer import VPNPeer, VpnPeerStatus
from app.schemas.vpn_peer import L2tpPeerCreate, OvpnPeerCreate
from app.services.vpn_service import VpnServiceError, create_l2tp_peer, create_ovpn_peer

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org/bot{token}"

NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,30}")

HELP_TEXT = (
    "🤖 <b>MikroTik Dashboard Bot</b>\n\n"
    "🔑 <b>Buat akun VPN</b>\n"
    "<code>/l2tp [nama]</code> — akun L2TP/IPsec baru\n"
    "<code>/ovpn [nama]</code> — akun OpenVPN baru (+ file .ovpn)\n"
    "<i>Nama opsional — kosongkan untuk auto-generate. Kalau ada lebih dari "
    "satu router: /l2tp &lt;router_id&gt; [nama]</i>\n\n"
    "📋 <b>Info</b>\n"
    "<code>/list</code> — daftar akun VPN yang sudah dibuat\n"
    "<code>/routers</code> — daftar router aktif\n"
    "<code>/help</code> — tampilkan pesan ini"
)

UNKNOWN_COMMAND_TEXT = (
    "❓ Perintah tidak dikenal.\n\n" "Ketik /help untuk lihat daftar perintah yang tersedia."
)

STATUS_EMOJI = {
    VpnPeerStatus.connected: "🟢",
    VpnPeerStatus.configured: "⚪",
    VpnPeerStatus.disconnected: "🔴",
    VpnPeerStatus.unknown: "⚫",
}


class TelegramBot:
    def __init__(self) -> None:
        self._offset = 0
        self._task: asyncio.Task | None = None
        self._client: httpx.AsyncClient | None = None

    def start(self) -> None:
        if not settings.telegram_bot_commands_enabled or not settings.telegram_bot_token:
            logger.info("Telegram bot commands disabled (set TELEGRAM_BOT_COMMANDS_ENABLED=true to enable)")
            return
        self._client = httpx.AsyncClient(base_url=API_BASE.format(token=settings.telegram_bot_token), timeout=40)
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Telegram bot command listener started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            await self._client.aclose()

    async def _poll_loop(self) -> None:
        assert self._client is not None
        while True:
            try:
                resp = await self._client.get("/getUpdates", params={"offset": self._offset, "timeout": 30})
                resp.raise_for_status()
                data = resp.json()
                for update in data.get("result", []):
                    self._offset = update["update_id"] + 1
                    await self._handle_update(update)
            except asyncio.CancelledError:
                raise
            except httpx.HTTPError as exc:
                logger.warning("Telegram polling error: %s", exc)
                await asyncio.sleep(5)
            except Exception:
                logger.exception("Unexpected error in Telegram bot loop")
                await asyncio.sleep(5)

    async def _handle_update(self, update: dict) -> None:
        message = update.get("message")
        if not message:
            return
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = (message.get("text") or "").strip()
        if not chat_id or not text:
            return

        if chat_id not in settings.telegram_allowed_chat_id_list:
            logger.warning("Telegram command from unauthorized chat_id=%s ignored: %s", chat_id, text)
            await self._send(chat_id, "🚫 Maaf, Anda tidak memiliki akses ke bot ini.")
            return

        command, *_ = text.split(maxsplit=1)
        command = command.split("@")[0].lower()  # strip "/cmd@BotName" group-chat suffix

        try:
            if command in ("/start", "/help"):
                await self._send(chat_id, HELP_TEXT)
            elif command == "/routers":
                await self._cmd_routers(chat_id)
            elif command == "/list":
                await self._cmd_list(chat_id, text)
            elif command == "/l2tp":
                await self._cmd_generate(chat_id, text, vpn_kind="l2tp")
            elif command in ("/ovpn", "/openvpn"):
                await self._cmd_generate(chat_id, text, vpn_kind="ovpn")
            elif command == "/generate":
                # Back-compat alias from the first version of this bot.
                await self._cmd_generate(chat_id, text, vpn_kind="l2tp")
            else:
                await self._send(chat_id, UNKNOWN_COMMAND_TEXT)
        except Exception:
            logger.exception("Error handling Telegram command: %s", text)
            await self._send(chat_id, "⚠️ Terjadi kesalahan saat memproses perintah. Coba lagi beberapa saat lagi.")

    async def _resolve_router(self, db, chat_id: str, parts: list[str]) -> tuple[Router | None, str | None]:
        """Shared router-selection logic for /l2tp, /ovpn, /list.
        Returns (router, remaining_arg) or (None, None) if a message was
        already sent to the user (no router, ambiguous choice, or bad ID)."""
        result = await db.execute(select(Router).where(Router.is_active.is_(True)))
        routers = list(result.scalars().all())

        if not routers:
            await self._send(chat_id, "📭 Belum ada router yang terdaftar di dashboard.")
            return None, None

        if parts and parts[0].isdigit():
            router_id = int(parts[0])
            router_obj = next((r for r in routers if r.id == router_id), None)
            if router_obj is None:
                await self._send(
                    chat_id,
                    f"❌ Router <code>{router_id}</code> tidak ditemukan.\nKetik /routers untuk lihat daftar ID.",
                )
                return None, None
            return router_obj, (parts[1] if len(parts) > 1 else None)

        if len(routers) == 1:
            return routers[0], (parts[0] if parts else None)

        await self._send(
            chat_id,
            "⚠️ Ada lebih dari satu router terdaftar, sebutkan ID-nya:\n"
            "<code>/l2tp &lt;router_id&gt; [nama]</code>\n\nKetik /routers untuk lihat daftar ID.",
        )
        return None, None

    async def _cmd_routers(self, chat_id: str) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Router).where(Router.is_active.is_(True)))
            routers = list(result.scalars().all())
        if not routers:
            await self._send(chat_id, "📭 Belum ada router yang terdaftar.")
            return
        lines = ["🌐 <b>Router aktif</b>"] + [
            f"<code>{r.id}</code> — {html.escape(r.name)} ({r.ip_address})" for r in routers
        ]
        await self._send(chat_id, "\n".join(lines))

    async def _cmd_list(self, chat_id: str, text: str) -> None:
        parts = text.split(maxsplit=2)[1:]
        async with AsyncSessionLocal() as db:
            router_obj, _ = await self._resolve_router(db, chat_id, parts)
            if router_obj is None:
                return
            result = await db.execute(
                select(VPNPeer)
                .where(VPNPeer.router_id == router_obj.id)
                .order_by(VPNPeer.vpn_type, VPNPeer.peer_name)
            )
            peers = list(result.scalars().all())

        if not peers:
            await self._send(chat_id, f"📭 Belum ada akun VPN di router <b>{html.escape(router_obj.name)}</b>.")
            return

        lines = [f"🔑 <b>VPN di {html.escape(router_obj.name)}</b>\n"]
        for p in peers:
            emoji = STATUS_EMOJI.get(p.status, "⚫")
            lines.append(f"{emoji} <code>{html.escape(p.peer_name)}</code> — {p.vpn_type.value} ({p.status.value})")
        await self._send(chat_id, "\n".join(lines))

    async def _cmd_generate(self, chat_id: str, text: str, vpn_kind: str) -> None:
        parts = text.split(maxsplit=2)[1:]  # drop the leading command word

        usage = (
            "<code>/l2tp [nama]</code> atau <code>/l2tp &lt;router_id&gt; [nama]</code>"
            if vpn_kind == "l2tp"
            else "<code>/ovpn [nama]</code> atau <code>/ovpn &lt;router_id&gt; [nama]</code>"
        )

        async with AsyncSessionLocal() as db:
            router_obj, name = await self._resolve_router(db, chat_id, parts)
            if router_obj is None:
                return

            if name and not NAME_PATTERN.fullmatch(name):
                await self._send(
                    chat_id,
                    f"❌ Nama tidak valid: <code>{html.escape(name)}</code>\n"
                    "Hanya huruf, angka, <code>-</code> dan <code>_</code>, maksimal 30 karakter.\n\n"
                    f"Format: {usage}",
                )
                return

            await self._send(chat_id, "⏳ Sedang membuat akun VPN, tunggu sebentar...")

            try:
                if vpn_kind == "l2tp":
                    result = await create_l2tp_peer(
                        db, router_obj, L2tpPeerCreate(username=name, description="Generated via Telegram"),
                        created_by_user_id=None,
                    )
                else:
                    result = await create_ovpn_peer(
                        db, router_obj, OvpnPeerCreate(username=name, description="Generated via Telegram"),
                        created_by_user_id=None,
                    )
            except VpnServiceError as exc:
                await self._send(
                    chat_id, f"❌ Gagal membuat VPN: {html.escape(str(exc))}\n\nFormat perintah: {usage}"
                )
                return

        if vpn_kind == "l2tp":
            message = (
                "✅ <b>VPN L2TP/IPsec berhasil dibuat!</b>\n\n"
                f"🌐 Server: <code>{result.server_address}</code>\n"
                f"👤 Username: <code>{result.username}</code>\n"
                f"🔒 Password: <code>{result.password}</code>\n"
                f"🔑 IPsec PSK: <code>{result.ipsec_psk}</code>\n\n"
                "📱 <i>Setting di HP: Settings → VPN → Tambah → Tipe L2TP/IPSec PSK, "
                "isi data di atas.</i>"
            )
            await self._send(chat_id, message)
        else:
            message = (
                "✅ <b>Akun OpenVPN berhasil dibuat!</b>\n\n"
                f"👤 Username: <code>{result.username}</code>\n"
                f"🔒 Password: <code>{result.password}</code>\n\n"
                "📎 File konfigurasi terlampir di bawah ini — import ke app "
                "<b>OpenVPN Connect</b>, lalu connect pakai username/password di atas."
            )
            await self._send(chat_id, message)
            await self._send_document(
                chat_id, filename=f"{result.peer.peer_name}.ovpn", content=result.config_text.encode()
            )

    async def _send(self, chat_id: str, text: str) -> None:
        if not self._client:
            return
        try:
            resp = await self._client.post(
                "/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            )
            if resp.status_code >= 400:
                logger.warning("Telegram sendMessage rejected (%s): %s", resp.status_code, resp.text)
        except httpx.HTTPError as exc:
            logger.warning("Failed to send Telegram message: %s", exc)

    async def _send_document(self, chat_id: str, filename: str, content: bytes) -> None:
        if not self._client:
            return
        try:
            resp = await self._client.post(
                "/sendDocument",
                data={"chat_id": chat_id},
                files={"document": (filename, content, "application/octet-stream")},
            )
            if resp.status_code >= 400:
                logger.warning("Telegram sendDocument rejected (%s): %s", resp.status_code, resp.text)
        except httpx.HTTPError as exc:
            logger.warning("Failed to send Telegram document: %s", exc)


telegram_bot = TelegramBot()
