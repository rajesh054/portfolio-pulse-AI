import pandas as pd
from portfolio_pulse.signals.shadow import evaluate

def test_shadow_never_requests_live_action():
    df = pd.DataFrame({"Close": [100, 101, 100, 102, 101, 103, 104, 105, 106, 120], "Volume": [100]*9 + [500]})
    report = evaluate(symbol="TEST", title="Large order win", history=df, source_type="NSE")
    assert report.action == "SHADOW_ONLY"
    assert 0 <= report.ai_score <= 100
    assert report.anomaly["score"] > 0

def test_shadow_handles_missing_optional_inputs():
    report = evaluate(symbol="TEST", title="Routine compliance report")
    assert report.action == "SHADOW_ONLY"
    assert report.relative_strength is None
    assert report.portfolio_risk is None
