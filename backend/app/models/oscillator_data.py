"""OscillatorData model — stores NetBrute and Intenciones values per asset."""

from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base


class OscillatorData(Base):
    __tablename__ = "oscillator_data"

    # Integer PK for TimescaleDB hypertable compatibility
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)

    # Which oscillator: "NETBRUTE" | "INTENTIONS"
    oscillator_type = Column(String(12), nullable=False)

    # Core value: -100 to +100 for NetBrute, 0 to 100 for RSI-based Intenciones
    value = Column(Numeric(10, 4), nullable=False)

    # "BULLISH" | "BEARISH" | "NONE"
    cross_type = Column(String(8), nullable=False, default="NONE")

    # "OVERBOUGHT" | "BULLISH" | "BEARISH" | "OVERSOLD"
    zone = Column(String(12), nullable=False)

    # Deterministic text description — no LLM
    observation = Column(String(500), nullable=False)

    # 0.0 - 100.0
    confidence_level = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (
        Index("idx_oscillator_asset_time", "asset_id", time.desc()),
        Index("idx_oscillator_asset_type", "asset_id", "oscillator_type"),
    )
