"""ambulance_dispatch: ambulances, dispatches

Revision ID: 0004_ambulance_dispatch
Revises: 0003_ai_triage
Create Date: 2026-07-17
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_ambulance_dispatch"
down_revision: str | None = "0003_ai_triage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ambulances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("callsign", sa.String(length=32), nullable=False),
        sa.Column("plate", sa.String(length=32), nullable=True),
        sa.Column("brigade_type", sa.String(length=64), nullable=False, server_default="umumiy"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="available"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("last_location_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_call_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["current_call_id"], ["emergency_calls.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ambulances_id", "ambulances", ["id"])
    op.create_index("ix_ambulances_callsign", "ambulances", ["callsign"], unique=True)
    op.create_index("ix_ambulances_status", "ambulances", ["status"])
    op.create_index("ix_ambulances_current_call_id", "ambulances", ["current_call_id"])

    op.create_table(
        "dispatches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_id", sa.Integer(), nullable=False),
        sa.Column("ambulance_id", sa.Integer(), nullable=False),
        sa.Column("assigned_by_id", sa.Integer(), nullable=True),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("eta_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["emergency_calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ambulance_id"], ["ambulances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_dispatches_id", "dispatches", ["id"])
    op.create_index("ix_dispatches_call_id", "dispatches", ["call_id"])
    op.create_index("ix_dispatches_ambulance_id", "dispatches", ["ambulance_id"])
    op.create_index("ix_dispatches_status", "dispatches", ["status"])


def downgrade() -> None:
    op.drop_table("dispatches")
    op.drop_table("ambulances")
