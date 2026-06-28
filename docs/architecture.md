# Architecture

Vitta Quant AI is organized as a modular research and trading platform.

## Backend

The FastAPI backend exposes versioned APIs and delegates work to domain services:

- Authentication
- Market data
- AI predictions
- Backtesting
- Trade history

The API layer should remain thin. Business behavior belongs in services, persistence belongs in repositories, and database tables belong in models.

## AI Module

The AI package is isolated from API concerns:

- Data preprocessing
- Feature engineering
- Training
- Inference
- Confidence scoring

Version 1 keeps these as interfaces and placeholders so trading logic can be added intentionally.

## Backtesting

The backtesting module is independent from live trading. It will own historical replay, execution simulation, metrics, and reports.

## Frontend

The React dashboard is structured around user workflows:

- Market overview
- Stock scanner
- AI recommendations
- Portfolio
- Backtesting
- Settings
