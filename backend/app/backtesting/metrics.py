from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestMetrics:
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
