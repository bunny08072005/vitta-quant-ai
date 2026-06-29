from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    def fetch_history(
        self,
        symbol: str,
        start_datetime: datetime,
        end_datetime: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Return OHLCV history indexed by trade datetime."""


class YahooFinanceProvider(MarketDataProvider):
    name = "yahoo"

    def fetch_history(
        self,
        symbol: str,
        start_datetime: datetime,
        end_datetime: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        import yfinance as yf

        start = start_datetime.isoformat()
        end = end_datetime.isoformat()

        data = yf.download(
            symbol,
            start=start,
            end=end,
            interval=interval,
            actions=False,
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=False,
        )

        if data.empty:
            return data

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.rename(
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
        data.index = pd.to_datetime(data.index)
        data.index.name = "trade_datetime"
        return data
