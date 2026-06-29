from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from app.market_data.errors import MarketDataValidationError
from app.market_data.intervals import validate_interval
from app.market_data.providers import MarketDataProvider
from app.repositories.market_data_repository import MarketDataRepository


@dataclass
class DownloadResult:
    symbol: str
    interval: str
    rows_fetched: int
    rows_inserted: int
    rows_updated: int
    status: str
    message: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None


class MarketDataDownloader:
    def __init__(self, repository: MarketDataRepository, provider: MarketDataProvider) -> None:
        self.repository = repository
        self.provider = provider
        self.logger = logging.getLogger(self.__class__.__name__)

    def download_history(
        self,
        symbol: str,
        provider_symbol: str,
        start_datetime: datetime,
        end_datetime: datetime,
        interval: str,
        max_retries: int = 3,
    ) -> DownloadResult:
        interval = validate_interval(interval)
        self.logger.info(
            "Downloading history %s %s to %s for %s",
            interval,
            start_datetime,
            end_datetime,
            symbol,
        )

        attempt = 1
        raw_data: pd.DataFrame | None = None
        while True:
            try:
                raw_data = self.provider.fetch_history(
                    provider_symbol,
                    start_datetime,
                    end_datetime,
                    interval,
                )
                break
            except Exception as exc:
                self.logger.warning(
                    "Download failed for %s %s (attempt %s/%s): %s",
                    provider_symbol,
                    interval,
                    attempt,
                    max_retries,
                    exc,
                    exc_info=True,
                )
                if attempt >= max_retries:
                    message = str(exc)
                    self.repository.log_update(
                        symbol=symbol,
                        provider=self.provider.name,
                        interval=interval,
                        status="failed",
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        message=message,
                    )
                    raise
                wait_seconds = min(2**attempt, 30)
                time.sleep(wait_seconds)
                attempt += 1

        if raw_data is None:
            raw_data = pd.DataFrame()

        price_records = self._to_price_records(symbol, raw_data, interval)
        inserted, updated = self.repository.upsert_prices(price_records)

        self.repository.log_update(
            symbol=symbol,
            provider=self.provider.name,
            interval=interval,
            status="success",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            rows_fetched=len(raw_data),
            rows_inserted=inserted,
            rows_updated=updated,
            message=None,
        )

        self.logger.info(
            "Downloaded %s %s rows for %s: inserted=%s updated=%s",
            symbol,
            interval,
            len(raw_data),
            inserted,
            updated,
        )

        return DownloadResult(
            symbol=symbol,
            interval=interval,
            rows_fetched=len(raw_data),
            rows_inserted=inserted,
            rows_updated=updated,
            status="success",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def _to_price_records(
        self,
        symbol: str,
        data: pd.DataFrame,
        interval: str,
    ) -> list[dict]:
        if data.empty:
            return []

        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        normalized_columns = {col.lower() for col in data.columns}
        if not required_columns <= set(col.title() for col in normalized_columns):
            missing_columns = required_columns - set(col.title() for col in normalized_columns)
            raise MarketDataValidationError(f"Missing required columns: {sorted(missing_columns)}")

        cleaned = data.copy()
        if isinstance(cleaned.columns, pd.MultiIndex):
            cleaned.columns = cleaned.columns.get_level_values(0)

        cleaned = cleaned.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adjusted_close",
                "Volume": "volume",
                "Dividends": "dividends",
                "Stock Splits": "stock_splits",
            }
        )

        cleaned.index = pd.to_datetime(cleaned.index)
        if cleaned.index.tz is not None:
            cleaned.index = cleaned.index.tz_convert("UTC").tz_localize(None)

        cleaned.index.name = "trade_datetime"
        cleaned["volume"] = cleaned["volume"].fillna(0)
        cleaned["dividends"] = cleaned.get("dividends", 0.0).fillna(0.0)
        cleaned["stock_splits"] = cleaned.get("stock_splits", 0.0).fillna(0.0)
        cleaned["adjusted_close"] = cleaned.get("adjusted_close")

        records: list[dict] = []
        now = datetime.utcnow()

        for trade_datetime, row in cleaned.iterrows():
            trade_date = trade_datetime.date()
            if pd.isna(row["open"]) or pd.isna(row["high"]) or pd.isna(row["low"]) or pd.isna(row["close"]):
                continue

            records.append(
                {
                    "symbol": symbol,
                    "exchange": "NSE",
                    "interval": interval,
                    "trade_datetime": trade_datetime,
                    "trade_date": trade_date,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "adjusted_close": None if pd.isna(row.get("adjusted_close")) else float(row["adjusted_close"]),
                    "volume": int(row["volume"]),
                    "dividends": 0.0 if pd.isna(row.get("dividends")) else float(row["dividends"]),
                    "stock_splits": 0.0 if pd.isna(row.get("stock_splits")) else float(row["stock_splits"]),
                    "provider": self.provider.name,
                    "created_at": now,
                    "updated_at": now,
                }
            )

        return records
