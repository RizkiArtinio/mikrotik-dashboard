"""add ssh_port to routers

Revision ID: 0003_ssh_port
Revises: 0002_wg_pool
Create Date: 2026-07-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_ssh_port"
down_revision: Union[str, None] = "0002_wg_pool"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("routers", sa.Column("ssh_port", sa.Integer(), nullable=False, server_default="22"))


def downgrade() -> None:
    op.drop_column("routers", "ssh_port")
