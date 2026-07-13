"""Inbound Telegram bot: lets whitelisted chat IDs generate L2TP VPN accounts
via chat commands (/generate). Separate from notifiers/telegram_notifier.py,
which only sends outbound alerts — this module also polls Telegram for
incoming messages.
"""

import asyncio
import logging
import re

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.router import Router
from app.schemas.vpn_peer import L2tpPeerCreate
from app.services.vpn_service import VpnServiceError, create_l2tp_peer

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org/bot{token}"

HELP_TEXT = (
    "*MikroTik Dashboard Bot*\n\n"
    "/generate <nama> — buat akun VPN L2TP baru\n"
    "/generate <router_id> <nama> — buat VPN di router tertentu (kalau ada lebih dari satu router)\n"
    "/routers — daftar router aktif\n"
    "/help — tampilkan bantuan ini"
)

NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,30}")


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
            await self._send(chat_id, "Maaf, Anda tidak memiliki akses ke bot ini.")
            return

        try:
            if text.startswith("/start") or text.startswith("/help"):
                await self._send(chat_id, HELP_TEXT)
            elif text.startswith("/routers"):
                await self._cmd_routers(chat_id)
            elif text.startswith("/generate"):
                await self._cmd_generate(chat_id, text)
            else:
                await self._send(chat_id, "Perintah tidak dikenal. Ketik /help untuk daftar perintah.")
        except Exception:
            logger.exception("Error handling Telegram command: %s", text)
            await self._send(chat_id, "Terjadi kesalahan saat memproses perintah.")

    async def _cmd_routers(self, chat_id: str) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Router).where(Router.is_active.is_(True)))
            routers = list(result.scalars().all())
        if not routers:
            await self._send(chat_id, "Belum ada router yang terdaftar.")
            return
        lines = ["*Router aktif:*"] + [f"`{r.id}` — {r.name} ({r.ip_address})" for r in routers]
        await self._send(chat_id, "\n".join(lines))

    async def _cmd_generate(self, chat_id: str, text: str) -> None:
        parts = text.split(maxsplit=2)[1:]  # drop the leading "/generate"

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Router).where(Router.is_active.is_(True)))
            routers = list(result.scalars().all())
            if not routers:
                await self._send(chat_id, "Belum ada router yang terdaftar.")
                return

            router_obj = None
            name: str | None = None

            if len(parts) == 2 and parts[0].isdigit():
                router_id = int(parts[0])
                router_obj = next((r for r in routers if r.id == router_id), None)
                name = parts[1]
                if router_obj is None:
                    await self._send(chat_id, f"Router {router_id} tidak ditemukan. Ketik /routers untuk daftar.")
                    return
            elif len(routers) == 1:
                router_obj = routers[0]
                name = parts[0] if parts else None
            else:
                await self._send(
                    chat_id,
                    "Ada lebih dari satu router terdaftar. Gunakan format:\n"
                    "`/generate <router_id> <nama>`\n\nKetik /routers untuk lihat daftar ID.",
                )
                return

            if name and not NAME_PATTERN.fullmatch(name):
                await self._send(chat_id, "Nama hanya boleh huruf, angka, - dan _, maksimal 30 karakter.")
                return

            try:
                peer_result = await create_l2tp_peer(
                    db,
                    router_obj,
                    L2tpPeerCreate(username=name, description="Generated via Telegram"),
                    created_by_user_id=None,
                )
            except VpnServiceError as exc:
                await self._send(chat_id, f"Gagal membuat VPN: {exc}")
                return

        message = (
            "*VPN L2TP/IPsec berhasil dibuat!*\n\n"
            f"Server: `{peer_result.server_address}`\n"
            f"Username: `{peer_result.username}`\n"
            f"Password: `{peer_result.password}`\n"
            f"IPsec PSK: `{peer_result.ipsec_psk}`\n\n"
            "Setting di HP: Settings → VPN → Tambah → Tipe *L2TP/IPSec PSK*, "
            "isi Server/Username/Password/IPsec pre-shared key sesuai di atas."
        )
        await self._send(chat_id, message)

    async def _send(self, chat_id: str, text: str) -> None:
        if not self._client:
            return
        try:
            await self._client.post("/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        except httpx.HTTPError as exc:
            logger.warning("Failed to send Telegram message: %s", exc)


telegram_bot = TelegramBot()
