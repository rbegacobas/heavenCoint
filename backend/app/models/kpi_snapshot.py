"""KPI Snapshot model — stores computed quantitative metrics per asset."""

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base


class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"

    # Use integer PK for TimescaleDB hypertable compatibility
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)

    # Price & volatility
    current_price = Column(Numeric(18, 8), nullable=False)
    atr_value = Column(Numeric(18, 8), nullable=False)
    atr_period = Column(SmallInteger, nullable=False, default=14)
    volatility_implied = Column(Numeric(8, 4))
    volatility_change_pct = Column(Numeric(8, 4))
    volatility_state = Column(String(12), nullable=False, default="stable")

    # Confidence ranges
    price_range_low_95 = Column(Numeric(18, 8))
    price_range_high_95 = Column(Numeric(18, 8))

    # Momentum
    momentum_value = Column(Numeric(8, 4))
    momentum_class = Column(String(10), nullable=False, default="neutral")

    # Trends
    trend_200d = Column(String(10))
    trend_134d = Column(String(10))
    trend_50d = Column(String(10))
    trend_divergence = Column(Boolean, nullable=False, default=False)

    # Expandable
    extra_kpis = Column(JSONB, default={})

    __table_args__ = (Index("idx_kpi_asset_time", "asset_id", time.desc()),)
