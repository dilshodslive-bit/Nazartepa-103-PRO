"""ai_triage: emergency_calls ga AI triaj ustunlari

Revision ID: 0003_ai_triage
Revises: 0002_emergency
Create Date: 2026-07-17
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_ai_triage"
down_revision: str | None = "0002_emergency"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "emergency_calls",
        sa.Column("priority_source", sa.String(length=32), nullable=True),
    )
    op.add_column("emergency_calls", sa.Column("ai_severity", sa.Integer(), nullable=True))
    op.add_column(
        "emergency_calls",
        sa.Column("ai_recommended_brigade", sa.String(length=64), nullable=True),
    )
    op.add_column("emergency_calls", sa.Column("ai_confidence", sa.Float(), nullable=True))
    op.add_column(
        "emergency_calls", sa.Column("ai_reason", sa.String(length=512), nullable=True)
    )
    op.add_column(
        "emergency_calls", sa.Column("ai_provider", sa.String(length=32), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("emergency_calls", "ai_provider")
    op.drop_column("emergency_calls", "ai_reason")
    op.drop_column("emergency_calls", "ai_confidence")
    op.drop_column("emergency_calls", "ai_recommended_brigade")
    op.drop_column("emergency_calls", "ai_severity")
    op.drop_column("emergency_calls", "priority_source")
