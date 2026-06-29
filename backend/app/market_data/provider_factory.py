from app.market_data.providers import MarketDataProvider, YahooFinanceProvider

_PROVIDERS: dict[str, type[MarketDataProvider]] = {
    "yahoo": YahooFinanceProvider,
}


def get_provider(name: str) -> MarketDataProvider:
    provider_cls = _PROVIDERS.get(name.strip().lower())
    if provider_cls is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unknown market data provider '{name}'. Supported providers: {supported}")
    return provider_cls()
