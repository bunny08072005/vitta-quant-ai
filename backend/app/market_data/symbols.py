from dataclasses import dataclass


@dataclass(frozen=True)
class DefaultSymbol:
    ticker: str
    name: str
    yahoo_symbol: str
    instrument_type: str = "equity"
    exchange: str = "NSE"


DEFAULT_SYMBOLS: tuple[DefaultSymbol, ...] = (
    DefaultSymbol("RELIANCE", "Reliance Industries", "RELIANCE.NS"),
    DefaultSymbol("TCS", "Tata Consultancy Services", "TCS.NS"),
    DefaultSymbol("INFY", "Infosys", "INFY.NS"),
    DefaultSymbol("HDFCBANK", "HDFC Bank", "HDFCBANK.NS"),
    DefaultSymbol("ICICIBANK", "ICICI Bank", "ICICIBANK.NS"),
    DefaultSymbol("SBIN", "State Bank of India", "SBIN.NS"),
    DefaultSymbol("ITC", "ITC", "ITC.NS"),
    DefaultSymbol("LT", "Larsen and Toubro", "LT.NS"),
    DefaultSymbol("BHARTIARTL", "Bharti Airtel", "BHARTIARTL.NS"),
    DefaultSymbol("NIFTY50", "NIFTY 50 Index", "^NSEI", "index"),
    DefaultSymbol("BANKNIFTY", "NIFTY Bank Index", "^NSEBANK", "index"),
)


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper().replace(".NS", "")


def to_yahoo_symbol(symbol: str) -> str:
    normalized = normalize_symbol(symbol)
    for configured in DEFAULT_SYMBOLS:
        if normalized in {configured.ticker, normalize_symbol(configured.yahoo_symbol)}:
            return configured.yahoo_symbol
    if normalized.startswith("^"):
        return normalized
    return f"{normalized}.NS"
