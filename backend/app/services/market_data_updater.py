from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta
from itertools import islice
from typing import Iterable

from app.market_data.intervals import DEFAULT_LOOKBACK, INTERVAL_DELTAS, SUPPORTED_INTERVALS, validate_interval
from app.market_data.symbols import normalize_symbol
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data_downloader import DownloadResult, MarketDataDownloader


def _chunked(iterable: Iterable[str], batch_size: int) -> Iterable[list[str]]:
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


class MarketDataUpdater:
    def __init__(self, repository: MarketDataRepository, downloader: MarketDataDownloader) -> None:
        self.repository = repository
        self.downloader = downloader
        self.logger = logging.getLogger(self.__class__.__name__)

    def update_missing_history(
        self,
        symbol: str,
        interval: str = "1d",
        start_date: date | None = None,
        end_date: date | None = None,
        max_retries: int = 3,
    ) -> DownloadResult | None:
        interval = validate_interval(interval)
        symbol_row = self.repository.ensure_symbol(symbol)
        normalized = normalize_symbol(symbol_row.ticker)

        start_datetime = self._to_datetime(start_date)
        end_datetime = self._to_datetime(end_date)

        if end_datetime is None:
            end_datetime = datetime.utcnow()
        elif isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_datetime = datetime.combine(end_date + timedelta(days=1), time.min)

        latest = self.repository.get_latest(normalized, interval=interval)
        if start_datetime is None:
            if latest is not None:
                start_datetime = latest.trade_datetime + INTERVAL_DELTAS[interval]
            else:
                start_datetime = end_datetime - DEFAULT_LOOKBACK[interval]
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_datetime = datetime.combine(start_date, time.min)

        if start_datetime > end_datetime:
            message = "No missing candles to update for the requested range."
            self.logger.info(
                "%s %s skipped: %s to %s",
                normalized,
                interval,
                start_datetime,
                end_datetime,
            )
            self.repository.log_update(
                symbol=normalized,
                provider=self.downloader.provider.name,
                interval=interval,
                status="skipped",
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                message=message,
            )
            return None

        self.logger.debug(
            "Updating missing history for %s %s from %s to %s",
            normalized,
            interval,
            start_datetime,
            end_datetime,
        )

        return self.downloader.download_history(
            symbol=normalized,
            provider_symbol=symbol_row.yahoo_symbol,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            interval=interval,
            max_retries=max_retries,
        )

    def update_symbols(
        self,
        symbols: list[str],
        interval: str = "1d",
        batch_size: int = 50,
        max_retries: int = 3,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DownloadResult | None]:
        interval = validate_interval(interval)
        results: list[DownloadResult | None] = []

        for batch in _chunked(symbols, batch_size):
            self.logger.info("Processing batch %s for interval %s", batch, interval)
            for symbol in batch:
                try:
                    results.append(
                        self.update_missing_history(
                            symbol,
                            interval=interval,
                            start_date=start_date,
                            end_date=end_date,
                            max_retries=max_retries,
                        )
                    )
                except Exception:
                    self.logger.exception("Failed to update symbol %s for interval %s", symbol, interval)
        return results

    def update_all_active_symbols(
        self,
        intervals: list[str] | None = None,
        batch_size: int = 50,
        max_retries: int = 3,
    ) -> list[DownloadResult | None]:
        intervals = intervals or list(SUPPORTED_INTERVALS)
        symbols = [symbol.ticker for symbol in self.repository.list_symbols()]

        results: list[DownloadResult | None] = []
        for interval in intervals:
            results.extend(
                self.update_symbols(
                    symbols,
                    interval=interval,
                    batch_size=batch_size,
                    max_retries=max_retries,
                )
            )

        return results

    @staticmethod
    def _to_datetime(value: date | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.combine(value, time.min)
