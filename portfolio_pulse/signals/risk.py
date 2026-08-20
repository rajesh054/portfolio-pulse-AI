"""Transparent portfolio concentration risk scoring."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PortfolioRisk:
    score: int
    level: str
    top_position_pct: float
    top_sector_pct: float
    concentration_score: int
    notes: tuple[str, ...]

def calculate(weights: dict[str,float], sectors: dict[str,str] | None = None) -> PortfolioRisk:
    clean={k:max(0.0,float(v)) for k,v in weights.items() if float(v)>0}; total=sum(clean.values())
    if total<=0: return PortfolioRisk(0,"UNKNOWN",0,0,0,())
    norm={k:v/total*100 for k,v in clean.items()}; top=max(norm.values()) if norm else 0
    sector_totals:dict[str,float]={}; sm=sectors or {}
    for sym,pct in norm.items(): sector_totals[sm.get(sym,"Unknown")]=sector_totals.get(sm.get(sym,"Unknown"),0)+pct
    top_sector=max(sector_totals.values()) if sector_totals else 0; score=0; notes=[]
    if top>=30: score+=45; notes.append(f"single position {top:.1f}%")
    elif top>=20: score+=30; notes.append(f"single position {top:.1f}%")
    elif top>=15: score+=15
    if top_sector>=50: score+=45; notes.append(f"sector concentration {top_sector:.1f}%")
    elif top_sector>=35: score+=30; notes.append(f"sector concentration {top_sector:.1f}%")
    elif top_sector>=25: score+=15
    score=min(100,score); level="HIGH" if score>=60 else "MODERATE" if score>=30 else "LOW"
    return PortfolioRisk(score,level,top,top_sector,score,tuple(notes))
