"""add oscillator_data table

Revision ID: a3e9f1b2c4d5
Revises: 57be196cbe30
Create Date: 2026-04-04 00:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a3e9f1b2c4d5"
down_revision: str | None = "57be196cbe30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oscillator_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "time",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("asset_id", postgresql.UUID(), nullable=False),
        sa.Column("oscillator_type", sa.String(length=12), nullable=False),
        sa.Column("value", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("cross_type", sa.String(length=8), nullable=False),
        sa.Column("zone", sa.String(length=12), nullable=False),
        sa.Column("observation", sa.String(length=500), nullable=False),
        sa.Column("confidence_level", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"],
            name=op.f("fk_oscillator_data_asset_id_assets"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oscillator_data")),
    )
    op.create_index(
        "idx_oscillator_asset_time",
        "oscillator_data",
        ["asset_id", sa.literal_column("time DESC")],
        unique=False,
    )
    op.create_index(
        "idx_oscillator_asset_type",
        "oscillator_data",
        ["asset_id", "oscillator_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_oscillator_asset_type", table_name="oscillator_data")
    op.drop_index("idx_oscillator_asset_time", table_name="oscillator_data")
    op.drop_table("oscillator_data")
