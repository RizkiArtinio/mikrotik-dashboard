from datetime import datetime, timezone
from typing import Any


def make_event(event_type: str, router_id: int, data: Any) -> dict:
    return {
        "type": event_type,
        "router_id": router_id,
        "data": data,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
