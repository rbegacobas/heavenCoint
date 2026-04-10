"""Pydantic schemas for assets endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AssetSearchResult(BaseModel):
    id: uuid.UUID | None = None
    ticker: str
    name: str
    asset_type: str
    exchange: str | None = None
    currency: str | None = None

    model_config = {"from_attributes": True}


class AssetSearchResponse(BaseModel):
    results: list[AssetSearchResult]
    count: int


class AssetLoadResponse(BaseModel):
    ticker: str
    asset_id: uuid.UUID
    status: str
    message: str


class PriceBar(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    model_config = {"from_attributes": True}
