"""Phase 1 shadow-mode aggregation.

Computes AI signals without altering existing alert delivery.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd
from .anomaly import detect
from .relative_strength import calculate as calculate_relative_strength
from .risk import calculate as calculate_portfolio_risk
from .severity import score_event

@dataclass(frozen=True)
class ShadowReport:
    symbol: str
    ai_score: int
    severity: dict[str, Any]
    anomaly: dict[str, Any]
    relative_strength: dict[str, Any] | None
    portfolio_risk: dict[str, Any] | None
    action: str = "SHADOW_ONLY"

def evaluate(*, symbol: str, title: str = "", history: pd.DataFrame | None = None, benchmark: pd.Series | None = None, weights: dict[str, float] | None = None, sectors: dict[str, str] | None = None, source_type: str = "") -> ShadowReport:
    severity = score_event(title, source_type=source_type)
    anomaly = detect(history) if history is not None else detect(pd.DataFrame())
    rs = None
    if history is not None and benchmark is not None and "Close" in history:
        rs = calculate_relative_strength(history["Close"], benchmark)
    risk = calculate_portfolio_risk(weights, sectors) if weights else None
    components = [severity.score, anomaly.score]
    if rs is not None: components.append(max(0, min(100, 50 + int(rs.alpha_pct * 5))))
    if risk is not None: components.append(max(0, 100 - risk.score))
    ai_score = round(sum(components) / len(components)) if components else 0
    return ShadowReport(symbol=symbol, ai_score=ai_score, severity=asdict(severity), anomaly=asdict(anomaly), relative_strength=asdict(rs) if rs else None, portfolio_risk=asdict(risk) if risk else None)
