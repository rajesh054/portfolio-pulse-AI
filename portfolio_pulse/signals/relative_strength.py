"""Relative strength versus a benchmark."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class RelativeStrength:
    stock_return_pct: float
    benchmark_return_pct: float
    alpha_pct: float
    outperforming: bool
    periods: dict[str, float]

def _ret(series: pd.Series, days: int) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) <= days: return 0.0
    return (float(s.iloc[-1]) / float(s.iloc[-1-days]) - 1) * 100

def calculate(stock: pd.Series, benchmark: pd.Series, *, days: int = 20) -> RelativeStrength:
    sr, br = _ret(stock, days), _ret(benchmark, days)
    periods = {str(d): _ret(stock,d)-_ret(benchmark,d) for d in (20,50,90) if len(stock.dropna())>d and len(benchmark.dropna())>d}
    return RelativeStrength(sr, br, sr-br, sr>br, periods)
