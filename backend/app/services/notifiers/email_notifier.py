import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.services.notifiers.base_notifier import Notifier

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    channel_name = "email"

    async def send(self, subject: str, message: str) -> bool:
        if not settings.email_enabled or not settings.smtp_host or not settings.alert_email_recipient_list:
            return False

        email = EmailMessage()
        email["From"] = settings.smtp_from_address or settings.smtp_username
        email["To"] = ", ".join(settings.alert_email_recipient_list)
        email["Subject"] = f"[MikroTik Dashboard] {subject}"
        email.set_content(message)

        try:
            await aiosmtplib.send(
                email,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username or None,
                password=settings.smtp_password or None,
                start_tls=settings.smtp_use_tls,
            )
            return True
        except Exception as exc:
            logger.error("Email notification failed: %s", exc)
            return False
