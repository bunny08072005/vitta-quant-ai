from datetime import date, datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import market_data  # noqa: F401
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data_service import MarketDataService
from app.market_data.errors import MarketDataValidationError


class FakeProvider:
    name = "fake"

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.calls: list[tuple[str, datetime, datetime, str]] = []

    def fetch_history(
        self,
        symbol: str,
        start_datetime: datetime,
        end_datetime: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        self.calls.append((symbol, start_datetime, end_datetime, interval))
        return self.data


def build_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


def price_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [100.0, 101.0],
            "high": [110.0, 111.0],
            "low": [95.0, 96.0],
            "close": [108.0, 109.0],
            "adjusted_close": [107.5, 108.5],
            "volume": [1000, 1500],
            "dividends": [0.0, 1.0],
            "stock_splits": [0.0, 0.0],
        },
        index=[date(2024, 1, 1), date(2024, 1, 2)],
    )


def test_update_missing_history_inserts_prices_and_log() -> None:
    db = build_session()
    repository = MarketDataRepository(db)
    service = MarketDataService(repository, FakeProvider(price_frame()))

    service.update_missing_history("RELIANCE", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))

    prices = repository.get_history("RELIANCE")
    assert len(prices) == 2
    assert prices[0].symbol == "RELIANCE"
    assert prices[0].close == 108.0
    assert prices[1].dividends == 1.0


def test_upsert_prevents_duplicate_records() -> None:
    db = build_session()
    repository = MarketDataRepository(db)
    service = MarketDataService(repository, FakeProvider(price_frame()))

    service.update_missing_history("INFY", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))
    service.update_missing_history("INFY", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))

    assert len(repository.get_history("INFY")) == 2


def test_validation_drops_rows_missing_core_ohlc_values() -> None:
    db = build_session()
    repository = MarketDataRepository(db)
    data = price_frame()
    data.loc[date(2024, 1, 2), "close"] = None
    service = MarketDataService(repository, FakeProvider(data))

    service.update_missing_history("TCS", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))

    assert len(repository.get_history("TCS")) == 1


def test_validation_rejects_missing_required_columns() -> None:
    db = build_session()
    repository = MarketDataRepository(db)
    service = MarketDataService(repository, FakeProvider(pd.DataFrame({"close": [1.0]})))

    try:
        service.update_missing_history("SBIN", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))
    except MarketDataValidationError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected MarketDataValidationError")


def test_default_symbols_include_indices() -> None:
    db = build_session()
    repository = MarketDataRepository(db)

    symbols = {symbol.ticker: symbol.yahoo_symbol for symbol in repository.list_symbols()}

    assert symbols["NIFTY50"] == "^NSEI"
    assert symbols["BANKNIFTY"] == "^NSEBANK"
