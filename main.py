from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from models import Base, engine, SessionLocal, PlanArtifact, PlanSnapshot
from routes import router
from datetime import datetime
import json

load_dotenv()

app = FastAPI(title="Build Web App API", version="1.0.0")

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(PlanArtifact).count()
        if count == 0:
            seeds = [
                {
                    "name": "Maya Chen — Emergency Fund Sprint",
                    "source_text": "I bring home $4,800 per month, have $9,200 credit card debt, and want a 6-month emergency fund.",
                    "scenario": "baseline",
                    "summary": "Maya has moderate debt pressure with strong income stability. Priority is debt ladder plus emergency buffer automation.",
                    "items": [
                        "Monthly surplus target: $1,250",
                        "Debt payoff first phase: 9 months",
                        "Emergency fund milestone 1: $2,500 in 2 months",
                    ],
                    "score": 79,
                    "assumptions": [
                        "Income remains stable over next 12 months.",
                        "No major rent increase this year.",
                    ],
                },
                {
                    "name": "Andre Ruiz — Freelance Stability Plan",
                    "source_text": "Freelance videographer with uneven income, rent-heavy budget, goal is to stabilize cash flow and set quarterly tax reserves.",
                    "scenario": "cautious",
                    "summary": "Andre needs variability buffers and explicit tax reserve rules before aggressive debt goals.",
                    "items": [
                        "Set 20% tax reserve on each invoice",
                        "Weekly owner-pay transfer to smooth income",
                        "Build 2-month minimum cash buffer first",
                    ],
                    "score": 64,
                    "assumptions": [
                        "Assumed uneven income with seasonal volatility.",
                        "Assumed rent remains fixed for next lease period.",
                    ],
                },
            ]
            for s in seeds:
                artifact = PlanArtifact(
                    name=s["name"],
                    source_text=s["source_text"],
                    active_scenario=s["scenario"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(artifact)
                db.flush()
                snapshot = PlanSnapshot(
                    artifact_id=artifact.id,
                    scenario=s["scenario"],
                    summary=s["summary"],
                    items_json=json.dumps(s["items"]),
                    score=s["score"],
                    assumptions_json=json.dumps(s["assumptions"]),
                    created_at=datetime.utcnow(),
                )
                db.add(snapshot)
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1' />
        <title>Build Web App API</title>
        <style>
          body { background:#0b1220; color:#e5e7eb; font-family: Inter, Arial, sans-serif; margin:0; }
          .wrap { max-width:980px; margin:40px auto; padding:24px; }
          .card { background:#111827; border:1px solid #1f2937; border-radius:14px; padding:20px; margin-bottom:16px; }
          h1 { margin-top:0; color:#f9fafb; }
          a { color:#93c5fd; text-decoration:none; }
          code { color:#a7f3d0; }
          ul { line-height:1.7; }
          .muted { color:#9ca3af; }
        </style>
      </head>
      <body>
        <div class='wrap'>
          <div class='card'>
            <h1>Build Web App — Personal Finance Planning API</h1>
            <p>Turn messy money details into a clear personal financial plan you can act on today.</p>
            <p class='muted'>Artifact-first workflow with assumption notes, scenario recomposition, and saved snapshot history.</p>
          </div>
          <div class='card'>
            <h2>Endpoints</h2>
            <ul>
              <li><code>GET /health</code> — service health</li>
              <li><code>POST /plan</code> and <code>POST /api/plan</code> — build financial brief from messy input</li>
              <li><code>POST /insights</code> and <code>POST /api/insights</code> — AI coaching insights for selected plan context</li>
              <li><code>POST /artifacts/save</code> and <code>POST /api/artifacts/save</code> — save named planning artifact</li>
              <li><code>GET /artifacts</code> and <code>GET /api/artifacts</code> — artifact library list</li>
              <li><code>POST /scenario/recompose</code> and <code>POST /api/scenario/recompose</code> — scenario switch with recomposed outputs</li>
            </ul>
          </div>
          <div class='card'>
            <h2>Tech Stack</h2>
            <ul>
              <li>FastAPI 0.115.0 + Uvicorn 0.30.0</li>
              <li>SQLAlchemy 2.0.35 (sync) + PostgreSQL/SQLite</li>
              <li>DigitalOcean Serverless Inference (Claude 4.6 Sonnet) via HTTPX 0.27.0</li>
            </ul>
            <p><a href='/docs'>OpenAPI Docs</a> · <a href='/redoc'>ReDoc</a></p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
