# Market Data Engine

Milestone 2 adds a modular market data engine for Indian market development data.

## Responsibilities

- Maintain a symbol master for NSE equities and indices.
- Fetch historical OHLCV data from Yahoo Finance through yfinance.
- Store historical prices in PostgreSQL.
- Prevent duplicate daily price rows with a symbol/date unique constraint.
- Capture adjusted close, dividends, and stock split fields when Yahoo provides them.
- Log every update attempt, including skipped and failed runs.
- Keep provider integration behind an interface so Zerodha, Upstox, Angel One, or another vendor can be added later.

## API

All endpoints are versioned under /api/v1. Direct aliases are also available at /market for local development.

- GET /api/v1/market/symbols
- GET /api/v1/market/history/{symbol}
- GET /api/v1/market/latest/{symbol}
- GET /api/v1/market/status

History query parameters:

- start_date: optional YYYY-MM-DD
- end_date: optional YYYY-MM-DD
- auto_update: defaults to true

## Scheduler

The scheduler is disabled by default. Enable it through environment variables:

MARKET_DATA_SCHEDULER_ENABLED=true
MARKET_DATA_SCHEDULER_INTERVAL_MINUTES=240

When enabled, FastAPI starts a background job that updates all configured active symbols.
