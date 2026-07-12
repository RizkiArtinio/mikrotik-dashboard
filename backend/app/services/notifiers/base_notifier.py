from abc import ABC, abstractmethod


class Notifier(ABC):
    channel_name: str

    @abstractmethod
    async def send(self, subject: str, message: str) -> bool:
        """Send a notification. Returns True on success, False otherwise
        (failures are logged by the implementation, never raised — a broken
        notification channel must not break the alert evaluation loop)."""
        raise NotImplementedError
