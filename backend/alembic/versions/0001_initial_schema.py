"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Each enum is used by exactly one table below, so its CREATE TYPE is emitted
# once, implicitly, as part of that table's CREATE TABLE (and DROP TYPE is
# emitted implicitly on DROP TABLE) — standard SQLAlchemy/Alembic behavior.
# Do not also call `.create()`/`.drop()` explicitly here: SQLAlchemy's
# table-create dispatch for Postgres ENUM columns issues CREATE TYPE
# unconditionally (ignoring `checkfirst`) whenever the type has no bound
# `metadata`, so an earlier explicit `.create()` collides with it
# (DuplicateObjectError on `CREATE TYPE ... already exists`).
vpn_type_enum = sa.Enum("wireguard", "l2tp", "sstp", "openvpn", "ipsec", name="vpntype")
vpn_status_enum = sa.Enum("connected", "disconnected", "configured", "unknown", name="vpnpeerstatus")
backup_type_enum = sa.Enum("backup", "rsc", name="backuptype")
backup_trigger_enum = sa.Enum("manual", "scheduled", name="backuptrigger")
user_role_enum = sa.Enum("super_admin", "network_engineer", "viewer", name="userrole")
alert_type_enum = sa.Enum(
    "router_down", "vpn_down", "cpu_high", "mem_high", "isp_down", name="alerttype"
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(150), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "routers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_encrypted", sa.String(512), nullable=False),
        sa.Column("api_port", sa.Integer(), nullable=False, server_default="8728"),
        sa.Column("use_ssl", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("site", sa.String(150), nullable=True),
        sa.Column("isp_gateway", sa.String(45), nullable=True),
        sa.Column("wireguard_endpoint", sa.String(255), nullable=True),
        sa.Column("snmp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("snmp_port", sa.Integer(), nullable=True),
        sa.Column("snmp_community_encrypted", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    op.create_table(
        "interfaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("router_id", sa.Integer(), sa.ForeignKey("routers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interface_name", sa.String(100), nullable=False),
        sa.Column("interface_type", sa.String(30), nullable=False, server_default="ether"),
        sa.Column("rx_bps", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tx_bps", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("rx_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tx_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("rx_packets", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tx_packets", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.UniqueConstraint("router_id", "interface_name", name="uq_interface_router_name"),
    )

    op.create_table(
        "vpn_peers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("router_id", sa.Integer(), sa.ForeignKey("routers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("peer_name", sa.String(150), nullable=False),
        sa.Column("vpn_type", vpn_type_enum, nullable=False),
        sa.Column("public_key", sa.String(255), nullable=True),
        sa.Column("allowed_ip", sa.String(100), nullable=True),
        sa.Column("endpoint", sa.String(255), nullable=True),
        sa.Column("dns", sa.String(100), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("remote_address", sa.String(45), nullable=True),
        sa.Column("status", vpn_status_enum, nullable=False, server_default="unknown"),
        sa.Column("rx_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tx_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    op.create_table(
        "traffic_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("router_id", sa.Integer(), sa.ForeignKey("routers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interface_name", sa.String(100), nullable=False),
        sa.Column("rx", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tx", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_traffic_history_router_iface_ts",
        "traffic_history",
        ["router_id", "interface_name", "timestamp"],
    )

    op.create_table(
        "backups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("router_id", sa.Integer(), sa.ForeignKey("routers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("backup_type", backup_type_enum, nullable=False),
        sa.Column("triggered_by", backup_trigger_enum, nullable=False, server_default="manual"),
        sa.Column("backup_date", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_type", alert_type_enum, nullable=False, unique=True),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("cooldown_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_telegram", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_email", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.String(255), nullable=True),
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("router_id", sa.Integer(), sa.ForeignKey("routers.id", ondelete="CASCADE"), nullable=True),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("dedup_key", sa.String(255), nullable=False),
        sa.Column("target_identifier", sa.String(150), nullable=True),
        sa.Column("message", sa.String(1000), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notification_logs_dedup_key", "notification_logs", ["dedup_key"])


def downgrade() -> None:
    # Dropping each table implicitly issues DROP TYPE for its enum column(s)
    # too (the mirror image of the implicit CREATE TYPE in upgrade()).
    op.drop_table("notification_logs")
    op.drop_table("alert_rules")
    op.drop_table("backups")
    op.drop_table("traffic_history")
    op.drop_table("vpn_peers")
    op.drop_table("interfaces")
    op.drop_table("routers")
    op.drop_table("users")
