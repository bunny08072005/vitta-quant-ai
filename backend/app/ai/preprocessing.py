import pandas as pd


class MarketDataPreprocessor:
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.copy()
