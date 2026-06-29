from __future__ import annotations

from datetime import timedelta

SUPPORTED_INTERVALS: tuple[str, ...] = ("1d", "1h", "15m", "5m", "1m")

DEFAULT_LOOKBACK: dict[str, timedelta] = {
    "1d": timedelta(days=365 * 5),
    "1h": timedelta(days=365),
    "15m": timedelta(days=90),
    "5m": timedelta(days=30),
    "1m": timedelta(days=7),
}

INTERVAL_DELTAS: dict[str, timedelta] = {
    "1d": timedelta(days=1),
    "1h": timedelta(hours=1),
    "15m": timedelta(minutes=15),
    "5m": timedelta(minutes=5),
    "1m": timedelta(minutes=1),
}


def validate_interval(interval: str) -> str:
    normalized = interval.strip().lower()
    if normalized not in SUPPORTED_INTERVALS:
        raise ValueError(f"Unsupported interval '{interval}'. Supported intervals: {SUPPORTED_INTERVALS}")
    return normalized


def to_timedelta(interval: str) -> timedelta:
    return INTERVAL_DELTAS[validate_interval(interval)]
