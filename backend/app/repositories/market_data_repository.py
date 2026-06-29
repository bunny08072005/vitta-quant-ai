from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.orm import Session

from app.market_data.symbols import DEFAULT_SYMBOLS, normalize_symbol, to_yahoo_symbol
from app.models.market_data import DataUpdateLog, HistoricalPrice, Symbol


class MarketDataRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_default_symbols(self) -> None:
        for item in DEFAULT_SYMBOLS:
            existing = self.get_symbol(item.ticker)
            if existing is None:
                self.db.add(
                    Symbol(
                        ticker=item.ticker,
                        name=item.name,
                        exchange=item.exchange,
                        yahoo_symbol=item.yahoo_symbol,
                        instrument_type=item.instrument_type,
                    )
                )
        self.db.commit()

    def list_symbols(self) -> list[Symbol]:
        self.seed_default_symbols()
        statement = select(Symbol).where(Symbol.is_active.is_(True)).order_by(Symbol.ticker)
        return list(self.db.scalars(statement).all())

    def get_symbol(self, symbol: str) -> Symbol | None:
        normalized = normalize_symbol(symbol)
        statement = select(Symbol).where((Symbol.ticker == normalized) | (Symbol.yahoo_symbol == symbol.upper()))
        return self.db.scalars(statement).first()

    def ensure_symbol(self, symbol: str) -> Symbol:
        normalized = normalize_symbol(symbol)
        existing = self.get_symbol(normalized)
        if existing is not None:
            return existing

        created = Symbol(
            ticker=normalized,
            name=normalized,
            exchange="NSE",
            yahoo_symbol=to_yahoo_symbol(normalized),
            instrument_type="equity",
        )
        self.db.add(created)
        self.db.commit()
        self.db.refresh(created)
        return created

    def get_history(
        self,
        symbol: str,
        interval: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[HistoricalPrice]:
        normalized = normalize_symbol(symbol)
        statement = select(HistoricalPrice).where(HistoricalPrice.symbol == normalized)

        if interval is not None:
            statement = statement.where(HistoricalPrice.interval == interval)
        if start_datetime is not None:
            statement = statement.where(HistoricalPrice.trade_datetime >= start_datetime)
        if end_datetime is not None:
            statement = statement.where(HistoricalPrice.trade_datetime <= end_datetime)

        statement = statement.order_by(HistoricalPrice.trade_datetime)
        return list(self.db.scalars(statement).all())

    def get_latest(self, symbol: str, interval: str | None = None) -> HistoricalPrice | None:
        normalized = normalize_symbol(symbol)
        statement = select(HistoricalPrice).where(HistoricalPrice.symbol == normalized)
        if interval is not None:
            statement = statement.where(HistoricalPrice.interval == interval)
        statement = statement.order_by(HistoricalPrice.trade_datetime.desc()).limit(1)
        return self.db.scalars(statement).first()

    def get_last_trade_datetime(self, symbol: str, interval: str | None = None) -> datetime | None:
        latest = self.get_latest(symbol, interval=interval)
        return latest.trade_datetime if latest is not None else None

    def upsert_prices(self, prices: list[dict]) -> tuple[int, int]:
        if not prices:
            return 0, 0

        inserted = 0
        updated = 0
        dialect = self.db.bind.dialect.name if self.db.bind is not None else ""

        if dialect == "postgresql":
            statement = postgres_insert(HistoricalPrice).values(prices)
            update_columns = {
                "open": statement.excluded.open,
                "high": statement.excluded.high,
                "low": statement.excluded.low,
                "close": statement.excluded.close,
                "adjusted_close": statement.excluded.adjusted_close,
                "volume": statement.excluded.volume,
                "dividends": statement.excluded.dividends,
                "stock_splits": statement.excluded.stock_splits,
                "provider": statement.excluded.provider,
                "updated_at": statement.excluded.updated_at,
            }
            self.db.execute(
                statement.on_conflict_do_update(
                    constraint="uq_historical_prices_symbol_interval_trade_datetime",
                    set_=update_columns,
                )
            )
            self.db.commit()
            return len(prices), 0

        for price in prices:
            existing = self.db.scalars(
                select(HistoricalPrice).where(
                    HistoricalPrice.symbol == price["symbol"],
                    HistoricalPrice.interval == price["interval"],
                    HistoricalPrice.trade_datetime == price["trade_datetime"],
                )
            ).first()
            if existing is None:
                self.db.add(HistoricalPrice(**price))
                inserted += 1
            else:
                for key, value in price.items():
                    setattr(existing, key, value)
                updated += 1
        self.db.commit()
        return inserted, updated

    def log_update(
        self,
        *,
        symbol: str,
        provider: str,
        status: str,
        interval: str = "1d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        rows_fetched: int = 0,
        rows_inserted: int = 0,
        rows_updated: int = 0,
        message: str | None = None,
    ) -> DataUpdateLog:
        log = DataUpdateLog(
            symbol=normalize_symbol(symbol),
            provider=provider,
            status=status,
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            rows_fetched=rows_fetched,
            rows_inserted=rows_inserted,
            rows_updated=rows_updated,
            message=message,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
