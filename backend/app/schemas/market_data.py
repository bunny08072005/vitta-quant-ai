from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MarketDataStatusResponse(BaseModel):
    provider: str | None
    ready: bool


class SymbolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    name: str
    exchange: str
    yahoo_symbol: str
    instrument_type: str
    is_active: bool


class HistoricalPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    exchange: str
    interval: str
    trade_datetime: datetime
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = None
    volume: int
    dividends: float
    stock_splits: float
    provider: str


class LatestPriceResponse(HistoricalPriceResponse):
    pass


class HistoryResponse(BaseModel):
    symbol: str
    interval: str
    start_date: date | None = None
    end_date: date | None = None
    count: int
    data: list[HistoricalPriceResponse]


class DataUpdateLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    provider: str
    status: str
    interval: str | None = None
    start_datetime: datetime | None
    end_datetime: datetime | None
    rows_fetched: int
    rows_inserted: int
    rows_updated: int
    message: str | None
    created_at: datetime


class MarketHistoryQuery(BaseModel):
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    auto_update: bool = True
