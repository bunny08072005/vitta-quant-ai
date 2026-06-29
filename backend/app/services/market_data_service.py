from datetime import date, datetime, time

from app.market_data.provider_factory import get_provider
from app.market_data.providers import MarketDataProvider
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data_downloader import MarketDataDownloader
from app.services.market_data_updater import MarketDataUpdater


class MarketDataService:
    def __init__(
        self,
        repository: MarketDataRepository,
        provider: MarketDataProvider | str | None = None,
    ) -> None:
        self.repository = repository
        if provider is None:
            self.provider = get_provider("yahoo")
        elif isinstance(provider, str):
            self.provider = get_provider(provider)
        else:
            self.provider = provider

        self.downloader = MarketDataDownloader(repository, self.provider)
        self.updater = MarketDataUpdater(repository, self.downloader)

    def is_ready(self) -> bool:
        return True

    def list_symbols(self):
        return self.repository.list_symbols()

    def get_history(
        self,
        symbol: str,
        interval: str = "1d",
        start_date: date | None = None,
        end_date: date | None = None,
        auto_update: bool = True,
    ):
        if auto_update:
            self.updater.update_missing_history(
                symbol,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
            )

        start_datetime = (
            datetime.combine(start_date, time.min) if start_date is not None else None
        )
        end_datetime = (
            datetime.combine(end_date, time.max) if end_date is not None else None
        )

        return self.repository.get_history(
            symbol,
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def get_latest(
        self,
        symbol: str,
        interval: str = "1d",
        auto_update: bool = True,
    ):
        if auto_update:
            self.updater.update_missing_history(symbol, interval=interval)
        return self.repository.get_latest(symbol, interval=interval)

    def update_missing_history(
        self,
        symbol: str,
        interval: str = "1d",
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        return self.updater.update_missing_history(
            symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def update_all_active_symbols(
        self,
        intervals: list[str] | None = None,
        batch_size: int = 50,
        max_retries: int = 3,
    ):
        return self.updater.update_all_active_symbols(
            intervals=intervals,
            batch_size=batch_size,
            max_retries=max_retries,
        )
