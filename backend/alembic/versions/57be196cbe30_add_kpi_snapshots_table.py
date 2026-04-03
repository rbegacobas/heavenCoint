"""add kpi_snapshots table

Revision ID: 57be196cbe30
Revises: 26414e5db68c
Create Date: 2026-04-03 13:01:40.535739

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "57be196cbe30"
down_revision: str | None = "26414e5db68c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "kpi_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "time", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False
        ),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("current_price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("atr_value", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("atr_period", sa.SmallInteger(), nullable=False),
        sa.Column("volatility_implied", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("volatility_change_pct", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("volatility_state", sa.String(length=12), nullable=False),
        sa.Column("price_range_low_95", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("price_range_high_95", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("momentum_value", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("momentum_class", sa.String(length=10), nullable=False),
        sa.Column("trend_200d", sa.String(length=10), nullable=True),
        sa.Column("trend_134d", sa.String(length=10), nullable=True),
        sa.Column("trend_50d", sa.String(length=10), nullable=True),
        sa.Column("trend_divergence", sa.Boolean(), nullable=False),
        sa.Column("extra_kpis", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["asset_id"], ["assets.id"], name=op.f("fk_kpi_snapshots_asset_id_assets")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kpi_snapshots")),
    )
    op.create_index(
        "idx_kpi_asset_time",
        "kpi_snapshots",
        ["asset_id", sa.literal_column("time DESC")],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_kpi_asset_time", table_name="kpi_snapshots")
    op.drop_table("kpi_snapshots")
