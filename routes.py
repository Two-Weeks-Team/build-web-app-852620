import json
import math
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import SessionLocal, PlanArtifact, PlanSnapshot
from ai_service import build_structured_brief, generate_insights

router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: Optional[str] = "baseline"


class InsightsRequest(BaseModel):
    selection: str
    context: str


class SaveArtifactRequest(BaseModel):
    name: str
    query: str
    preferences: Optional[str] = "baseline"


class ScenarioRequest(BaseModel):
    artifact_id: int
    scenario: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _extract_amounts(text: str):
    nums = re.findall(r"\$?\d+[\d,]*(?:\.\d+)?", text)
    cleaned = []
    for n in nums:
        try:
            cleaned.append(float(n.replace("$", "").replace(",", "")))
        except Exception:
            pass
    return cleaned


def _deterministic_plan(query: str, preferences: str):
    q = query.lower()
    amounts = _extract_amounts(query)
    monthly_income = max([a for a in amounts if a < 20000], default=4800.0)
    debt_total = sum([a for a in amounts if 1000 <= a <= 150000])
    if debt_total == 0:
        debt_total = 9200.0 if "credit" in q else 24000.0 if "loan" in q else 12000.0

    spend_ratio = 0.7
    if "rent-heavy" in q or "rent heavy" in q:
        spend_ratio = 0.82
    if "aggressive" in preferences.lower():
        spend_ratio -= 0.08
    if "cautious" in preferences.lower():
        spend_ratio += 0.06

    monthly_spend = monthly_income * min(max(spend_ratio, 0.45), 0.9)
    monthly_surplus = monthly_income - monthly_spend

    if "freelance" in q or "uneven" in q or "irregular" in q:
        confidence = 62
        assumptions = [
            "Assumed average monthly income based on uneven earnings.",
            "Added a 15% tax reserve before discretionary allocations.",
        ]
        monthly_surplus *= 0.85
    else:
        confidence = 78
        assumptions = [
            "Assumed stated income remains stable for the next 12 months.",
            "Assumed minimum debt payments are already included in spending.",
        ]

    if monthly_surplus < 0:
        monthly_surplus = 0
        confidence -= 10
        assumptions.append("Current spending appears above income; plan uses stabilization first.")

    emergency_target = monthly_spend * 6
    months_to_efund = math.ceil(emergency_target / monthly_surplus) if monthly_surplus > 0 else 999
    debt_payoff_months = math.ceil(debt_total / (monthly_surplus * 0.65)) if monthly_surplus > 0 else 999

    top_priority = "Build emergency buffer"
    if debt_total > emergency_target * 0.6:
        top_priority = "Start debt payoff ladder"

    items = [
        f"Monthly take-home estimate: ${monthly_income:,.0f}",
        f"Monthly spending estimate: ${monthly_spend:,.0f}",
        f"Projected monthly surplus: ${monthly_surplus:,.0f}",
        f"Debt payoff runway: ~{debt_payoff_months} months",
        f"Emergency fund target (6 months): ${emergency_target:,.0f} (~{months_to_efund} months)",
        "This week: open a dedicated plan account and auto-transfer first surplus amount.",
        "This month: implement the highest-interest debt extra payment rule.",
        "Next 90 days: review scenario changes and adjust reserve percentages.",
    ]

    summary = (
        f"Your {preferences} plan shows a monthly surplus near ${monthly_surplus:,.0f}. "
        f"Priority: {top_priority.lower()}. Debt pressure is {'high' if debt_total > 15000 else 'moderate'}, "
        "and the plan includes explicit assumption notes for uncertain inputs."
    )

    return {
        "summary": summary,
        "items": items,
        "score": max(35, min(95, confidence)),
        "assumptions": assumptions,
        "cashflow_monthly": round(monthly_surplus, 2),
        "debt_total": round(debt_total, 2),
        "emergency_fund_target": round(emergency_target, 2),
        "top_priority": top_priority,
    }


def _scenario_multiplier(scenario: str):
    s = (scenario or "baseline").lower()
    if s == "cautious":
        return 0.8
    if s == "aggressive":
        return 1.2
    return 1.0


@router.post("/plan")
@router.post("/plan")
async def build_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    base = _deterministic_plan(payload.query, payload.preferences or "baseline")
    ai = await build_structured_brief(payload.query, payload.preferences or "baseline")

    if ai.get("ok") and isinstance(ai.get("data"), dict):
        data = ai["data"]
        summary = data.get("summary") or base["summary"]
        items = data.get("items") if isinstance(data.get("items"), list) else base["items"]
        score = data.get("score") if isinstance(data.get("score"), int) else base["score"]
        assumptions = data.get("assumptions") if isinstance(data.get("assumptions"), list) else base["assumptions"]
        result = {"summary": summary, "items": items, "score": score, "assumptions": assumptions, "note": ai.get("note", "")}
    else:
        result = {"summary": base["summary"], "items": base["items"], "score": base["score"], "assumptions": base["assumptions"], "note": ai.get("note", "")}

    return result


@router.post("/insights")
@router.post("/insights")
async def insights(payload: InsightsRequest):
    ai = await generate_insights(payload.selection, payload.context)
    if ai.get("ok") and isinstance(ai.get("data"), dict):
        data = ai["data"]
        return {
            "insights": data.get("insights", []),
            "next_actions": data.get("next_actions", []),
            "highlights": data.get("highlights", []),
            "note": ai.get("note", "AI response generated."),
        }

    fallback = {
        "insights": [
            "Focus on cash-flow reliability before adding new goals.",
            "Use scenario testing to avoid over-committing surplus.",
        ],
        "next_actions": [
            "Set one automatic weekly transfer to a reserve account.",
            "List all debt APRs and mark the top two targets.",
        ],
        "highlights": [
            "Assumptions are visible and editable.",
            "Plan remains actionable even with incomplete inputs.",
        ],
        "note": ai.get("note", "AI is temporarily unavailable."),
    }
    return fallback


@router.post("/artifacts/save")
@router.post("/artifacts/save")
async def save_artifact(payload: SaveArtifactRequest, db: Session = Depends(get_db)):
    computed = _deterministic_plan(payload.query, payload.preferences or "baseline")
    artifact = PlanArtifact(
        name=payload.name,
        source_text=payload.query,
        active_scenario=(payload.preferences or "baseline").lower(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(artifact)
    db.flush()

    snap = PlanSnapshot(
        artifact_id=artifact.id,
        scenario=(payload.preferences or "baseline").lower(),
        summary=computed["summary"],
        items_json=json.dumps(computed["items"]),
        score=int(computed["score"]),
        assumptions_json=json.dumps(computed["assumptions"]),
        created_at=datetime.utcnow(),
    )
    db.add(snap)
    db.commit()
    db.refresh(artifact)

    return {
        "artifact_id": artifact.id,
        "name": artifact.name,
        "saved_snapshot_id": snap.id,
        "scenario": snap.scenario,
        "created_at": artifact.created_at.isoformat(),
    }


@router.get("/artifacts")
@router.get("/artifacts")
def list_artifacts(db: Session = Depends(get_db)):
    artifacts = db.query(PlanArtifact).order_by(PlanArtifact.updated_at.desc()).all()
    result = []
    for a in artifacts:
        latest = db.query(PlanSnapshot).filter(PlanSnapshot.artifact_id == a.id).order_by(PlanSnapshot.created_at.desc()).first()
        result.append(
            {
                "artifact_id": a.id,
                "name": a.name,
                "active_scenario": a.active_scenario,
                "updated_at": a.updated_at.isoformat(),
                "latest_summary": latest.summary if latest else "",
                "latest_score": latest.score if latest else 0,
            }
        )
    return {"items": result}


@router.post("/scenario/recompose")
@router.post("/scenario/recompose")
def recompose_scenario(payload: ScenarioRequest, db: Session = Depends(get_db)):
    artifact = db.query(PlanArtifact).filter(PlanArtifact.id == payload.artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    base = _deterministic_plan(artifact.source_text, payload.scenario)
    factor = _scenario_multiplier(payload.scenario)
    adjusted_items = list(base["items"])
    adjusted_items.insert(0, f"Scenario '{payload.scenario}' applied with adjustment factor {factor:.2f}.")

    snap = PlanSnapshot(
        artifact_id=artifact.id,
        scenario=payload.scenario.lower(),
        summary=base["summary"],
        items_json=json.dumps(adjusted_items),
        score=int(max(30, min(95, round(base["score"] * factor)))),
        assumptions_json=json.dumps(base["assumptions"] + [f"Scenario switch applied: {payload.scenario.lower()}."]),
        created_at=datetime.utcnow(),
    )
    artifact.active_scenario = payload.scenario.lower()
    artifact.updated_at = datetime.utcnow()
    db.add(snap)
    db.commit()

    return {
        "artifact_id": artifact.id,
        "scenario": snap.scenario,
        "summary": snap.summary,
        "items": json.loads(snap.items_json),
        "score": snap.score,
        "assumptions": json.loads(snap.assumptions_json),
    }
