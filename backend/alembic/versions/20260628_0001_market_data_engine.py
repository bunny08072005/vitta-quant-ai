"""market data engine tables

Revision ID: 20260628_0001
Revises:
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260628_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "symbols",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("exchange", sa.String(length=16), nullable=False),
        sa.Column("yahoo_symbol", sa.String(length=32), nullable=False),
        sa.Column("instrument_type", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_symbols_exchange"), "symbols", ["exchange"], unique=False)
    op.create_index(op.f("ix_symbols_ticker"), "symbols", ["ticker"], unique=True)
    op.create_index(op.f("ix_symbols_yahoo_symbol"), "symbols", ["yahoo_symbol"], unique=True)

    op.create_table(
        "historical_prices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("exchange", sa.String(length=16), nullable=False),
        sa.Column("interval", sa.String(length=16), nullable=False),
        sa.Column("trade_datetime", sa.DateTime(), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("adjusted_close", sa.Float(), nullable=True),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column("dividends", sa.Float(), nullable=False),
        sa.Column("stock_splits", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "symbol",
            "interval",
            "trade_datetime",
            name="uq_historical_prices_symbol_interval_trade_datetime",
        ),
    )
    op.create_index(op.f("ix_historical_prices_symbol"), "historical_prices", ["symbol"], unique=False)
    op.create_index(op.f("ix_historical_prices_interval"), "historical_prices", ["interval"], unique=False)
    op.create_index(op.f("ix_historical_prices_trade_datetime"), "historical_prices", ["trade_datetime"], unique=False)

    op.create_table(
        "data_update_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("interval", sa.String(length=16), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=True),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("rows_fetched", sa.Integer(), nullable=False),
        sa.Column("rows_inserted", sa.Integer(), nullable=False),
        sa.Column("rows_updated", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_update_logs_created_at"), "data_update_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_data_update_logs_status"), "data_update_logs", ["status"], unique=False)
    op.create_index(op.f("ix_data_update_logs_symbol"), "data_update_logs", ["symbol"], unique=False)
    op.create_index(op.f("ix_data_update_logs_created_at"), "data_update_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_data_update_logs_status"), "data_update_logs", ["status"], unique=False)
    op.create_index(op.f("ix_data_update_logs_symbol"), "data_update_logs", ["symbol"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_update_logs_symbol"), table_name="data_update_logs")
    op.drop_index(op.f("ix_data_update_logs_status"), table_name="data_update_logs")
    op.drop_index(op.f("ix_data_update_logs_created_at"), table_name="data_update_logs")
    op.drop_table("data_update_logs")
    op.drop_index(op.f("ix_historical_prices_trade_date"), table_name="historical_prices")
    op.drop_index(op.f("ix_historical_prices_symbol"), table_name="historical_prices")
    op.drop_table("historical_prices")
    op.drop_index(op.f("ix_symbols_yahoo_symbol"), table_name="symbols")
    op.drop_index(op.f("ix_symbols_ticker"), table_name="symbols")
    op.drop_index(op.f("ix_symbols_exchange"), table_name="symbols")
    op.drop_table("symbols")
