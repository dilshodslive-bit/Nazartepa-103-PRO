"""emergency: emergency_calls, call_events

Revision ID: 0002_emergency
Revises: 0001_initial
Create Date: 2026-07-17
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_emergency"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "emergency_calls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("caller_phone", sa.String(length=32), nullable=False),
        sa.Column("caller_name", sa.String(length=255), nullable=True),
        sa.Column("address_text", sa.String(length=512), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("complaint", sa.Text(), nullable=False),
        sa.Column("media_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("priority", sa.String(length=32), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_emergency_calls_id", "emergency_calls", ["id"])
    op.create_index("ix_emergency_calls_status", "emergency_calls", ["status"])
    op.create_index("ix_emergency_calls_priority", "emergency_calls", ["priority"])
    op.create_index("ix_emergency_calls_created_by_id", "emergency_calls", ["created_by_id"])

    op.create_table(
        "call_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["emergency_calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_call_events_id", "call_events", ["id"])
    op.create_index("ix_call_events_call_id", "call_events", ["call_id"])
    op.create_index("ix_call_events_created_at", "call_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("call_events")
    op.drop_table("emergency_calls")
