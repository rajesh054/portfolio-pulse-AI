"""Deterministic event significance scoring for Phase 1."""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Severity:
    level: int
    name: str
    score: int
    reasons: tuple[str, ...]

_LEVELS = {0: "NOISE", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
_CRITICAL = ("auditor resignation", "qualified audit", "fraud", "default", "insolvency", "bankruptcy", "forensic audit", "going concern", "regulatory action", "sebi order", "trading suspension")
_HIGH = ("promoter pledge", "pledge invoked", "promoter resignation", "ceo resign", "cfo resign", "guidance cut", "guidance withdrawn", "order cancellation", "major acquisition", "debt restructuring", "credit rating downgrade", "investigation", "show cause notice", "large order", "order win", "fund raise", "rights issue", "preferential issue", "buyback")
_MEDIUM = ("financial results", "quarterly results", "dividend", "bonus", "split", "board meeting", "management change", "capex", "acquisition", "contract", "order", "insider", "promoter holding", "shareholding")
_LOW = ("analyst", "investor meet", "conference call", "presentation", "schedule", "compliance", "certificate", "newspaper", "trading window")

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def score_event(title: str, *, alert_type: str = "", category: str = "", source_type: str = "") -> Severity:
    text = _norm(" ".join((title, alert_type, category)))
    reasons: list[str] = []
    score = 20
    for phrase in _CRITICAL:
        if phrase in text: score = max(score, 95); reasons.append(phrase)
    for phrase in _HIGH:
        if phrase in text: score = max(score, 75); reasons.append(phrase)
    for phrase in _MEDIUM:
        if phrase in text: score = max(score, 50); reasons.append(phrase)
    for phrase in _LOW:
        if phrase in text and score < 50: score = min(score, 30); reasons.append(phrase)
    if _norm(source_type) in {"nse", "exchange", "company", "filing"}:
        score = min(100, score + 5); reasons.append("primary-source")
    if "routine" in text or "compliance report" in text:
        score = min(score, 20); reasons.append("routine")
    level = 4 if score >= 90 else 3 if score >= 70 else 2 if score >= 45 else 1 if score >= 25 else 0
    return Severity(level, _LEVELS[level], score, tuple(dict.fromkeys(reasons)))
