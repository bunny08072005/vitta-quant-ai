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
