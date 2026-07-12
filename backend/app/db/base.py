from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import every model module here so Alembic's autogenerate (which inspects
# Base.metadata) sees the full schema. Models themselves must not import this
# module in a way that creates a cycle — they only import `Base`.
from app.models import (  # noqa: E402,F401
    alert_rule,
    backup,
    interface,
    notification_log,
    router,
    traffic_history,
    user,
    vpn_peer,
)
