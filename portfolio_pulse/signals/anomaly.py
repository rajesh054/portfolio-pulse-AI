"""Price/volume anomaly detection using local OHLCV history."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Anomaly:
    score: int
    level: str
    return_pct: float
    relative_volume: float
    price_z: float
    volume_z: float
    reasons: tuple[str, ...]

def _z(value: float, series: pd.Series) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 5: return 0.0
    std = float(s.std(ddof=0))
    return 0.0 if std == 0 else (value - float(s.mean())) / std

def detect(history: pd.DataFrame, *, lookback: int = 20) -> Anomaly:
    if history is None or history.empty or "Close" not in history:
        return Anomaly(0, "NORMAL", 0.0, 0.0, 0.0, 0.0, ())
    close = pd.to_numeric(history["Close"], errors="coerce").dropna()
    if len(close) < 3: return Anomaly(0, "NORMAL", 0.0, 0.0, 0.0, 0.0, ())
    recent = close.tail(lookback + 1)
    ret = (float(recent.iloc[-1]) / float(recent.iloc[-2]) - 1.0) * 100
    returns = recent.pct_change().dropna() * 100
    price_z = _z(ret, returns.iloc[:-1])
    rel_vol = vol_z = 0.0
    if "Volume" in history:
        vol = pd.to_numeric(history["Volume"], errors="coerce").dropna()
        if len(vol) >= 6:
            base = vol.iloc[:-1].tail(lookback); latest = float(vol.iloc[-1]); mean = float(base.mean())
            rel_vol = latest / mean if mean > 0 else 0.0; vol_z = _z(latest, base)
    score = 0; reasons: list[str] = []
    if abs(ret) >= 2: score += min(35, int(abs(ret) * 4)); reasons.append(f"price move {ret:+.2f}%")
    if abs(price_z) >= 2: score += min(25, int(abs(price_z) * 6)); reasons.append(f"price z-score {price_z:+.1f}")
    if rel_vol >= 1.5: score += min(35, int((rel_vol - 1) * 25)); reasons.append(f"volume {rel_vol:.1f}x normal")
    if abs(vol_z) >= 2: score += min(15, int(abs(vol_z) * 3)); reasons.append(f"volume z-score {vol_z:+.1f}")
    score = min(100, score)
    level = "EXTREME" if score >= 75 else "HIGH" if score >= 50 else "WATCH" if score >= 25 else "NORMAL"
    return Anomaly(score, level, ret, rel_vol, price_z, vol_z, tuple(reasons))
