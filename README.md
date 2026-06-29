# Vitta Quant AI

AI-powered quantitative research and trading platform for the Indian stock market.

This repository is scaffolded for a scalable MVP foundation:

- FastAPI backend
- React + TypeScript frontend
- PostgreSQL database
- Modular AI and backtesting layers
- Docker Compose local environment

Trading logic is intentionally not implemented yet. The current focus is a clean, extensible platform structure.

## Project Layout

```text
backend/          FastAPI application and Python domain modules
frontend/         React + TypeScript dashboard
infrastructure/  Database and deployment support files
docs/            Architecture and implementation notes
scripts/         Developer utilities
```

## Quick Start

1. Copy `.env.example` to `.env`.
2. Start the stack:

```bash
docker compose up --build
```

Backend: `http://localhost:8000`

Frontend: `http://localhost:5173`

API docs: `http://localhost:8000/docs`

## Market Data Engine

Milestone 2 adds a market data engine for Indian equities and indices using yfinance for development data.

Run the stack:

```bash
docker compose up --build
```

Apply database migrations from inside the backend container or local backend environment:

```bash
alembic upgrade head
```

Useful endpoints:

Direct aliases also exist at `/market/...`, but the versioned `/api/v1/market/...` paths are preferred.

- `GET /api/v1/market/symbols`
- `GET /api/v1/market/history/RELIANCE?start_date=2024-01-01&end_date=2024-01-31`
- `GET /api/v1/market/latest/TCS`
- `GET /api/v1/market/status`

The first history/latest request can automatically download missing records, validate OHLCV rows, store them in PostgreSQL, and log the update. The live data layer is provider-based, so Zerodha, Upstox, Angel One, or another API can be plugged in later without changing the API layer.

Scheduler settings are available in `.env.example` and are disabled by default.
