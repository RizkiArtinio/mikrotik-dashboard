import logging

import httpx

from app.core.config import settings
from app.services.notifiers.base_notifier import Notifier

logger = logging.getLogger(__name__)


class TelegramNotifier(Notifier):
    channel_name = "telegram"

    async def send(self, subject: str, message: str) -> bool:
        if not settings.telegram_enabled or not settings.telegram_bot_token or not settings.telegram_chat_id:
            return False

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        text = f"*{subject}*\n{message}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    url, json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "Markdown"}
                )
                resp.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            logger.error("Telegram notification failed: %s", exc)
            return False
