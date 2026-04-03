"""Macro indicators model — FRED data."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    indicator_code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    indicator_name: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    previous_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    projection_90d: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    projection_365d: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    recession_probability: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    economic_cycle_phase: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="fred", nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
