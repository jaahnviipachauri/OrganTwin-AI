"""
OrganTwin AI API — FastAPI entrypoint.

Endpoints (all prefixed as implemented below):
  GET  /health
  GET  /api/live                 dashboard snapshot (organs, alerts, predictions)
  GET  /api/organs               organ twins
  GET  /api/organs/{name}
  GET  /api/compare              multi-organ comparison
  POST /api/drugs/apply          start exposure on one organ or all
  GET  /api/drugs                catalog
  GET  /api/drugs/ranking        toxicity ranking
  GET  /api/predictions
  GET  /api/alerts
  GET  /api/analytics/history
  GET  /api/analytics/trends
  GET  /api/experiments
  GET  /api/insights
  GET  /api/reports/experiment.pdf
  GET  /api/reports/fda.pdf
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import desc, select

from .config import CORS_ORIGINS, HISTORY_LIMIT
from .database import SessionLocal, init_db
from .models import Alert, Experiment, SensorReading
from .schemas import DrugApplyRequest, ExperimentOut
from .services.lab import lab
from .services.ml_engine import get_engine
from .services.organ_sim import DRUGS
from .services.reports import build_experiment_pdf, build_fda_style_pdf


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    get_engine()
    lab.start()
    yield
    lab.stop()


app = FastAPI(
    title="OrganTwin AI",
    description="Organ-on-chip digital twins with AI toxicity prediction.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "organtwin-ai"}


@app.get("/api/live")
def live():
    return lab.live()


@app.get("/api/organs")
def organs():
    return [lab.snapshot(c) for c in lab.chips.values()]


@app.get("/api/organs/{name}")
def organ_one(name: str):
    if name not in lab.chips:
        raise HTTPException(404, "Unknown organ")
    return lab.snapshot(lab.chips[name])


@app.get("/api/compare")
def compare():
    live_state = lab.live()
    return {
        "organs": live_state.organs,
        "predictions": live_state.predictions,
        "ranking_hint": "Use lower damage % and higher survival as preferred chips.",
    }


@app.get("/api/drugs")
def drugs():
    return [
        {"id": key, **meta}
        for key, meta in DRUGS.items()
    ]


@app.post("/api/drugs/apply", response_model=list[ExperimentOut])
def apply_drug(payload: DrugApplyRequest):
    try:
        created = lab.apply_drug(
            payload.organ,
            payload.drug,
            payload.dose_mg,
            payload.duration_h,
            payload.age_group,
            payload.experiment_name,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return created


@app.get("/api/drugs/ranking")
def ranking():
    return lab.ranking()


@app.get("/api/predictions")
def predictions():
    return lab.latest_predictions


@app.get("/api/alerts")
def alerts(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.scalars(select(Alert).order_by(desc(Alert.id)).limit(limit)).all()
        return [
            {
                "id": r.id,
                "organ": r.organ,
                "severity": r.severity,
                "kind": r.kind,
                "message": r.message,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    finally:
        db.close()


@app.get("/api/analytics/history")
def history(organ: str | None = None, metric: str | None = None, limit: int = HISTORY_LIMIT):
    db = SessionLocal()
    try:
        stmt = select(SensorReading).order_by(desc(SensorReading.id)).limit(limit * 8)
        if organ:
            stmt = stmt.where(SensorReading.organ == organ)
        if metric:
            stmt = stmt.where(SensorReading.metric == metric)
        rows = list(reversed(db.scalars(stmt).all()))
        return [
            {
                "id": r.id,
                "organ": r.organ,
                "metric": r.metric,
                "value": r.value,
                "unit": r.unit,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    finally:
        db.close()


@app.get("/api/analytics/trends")
def trends():
    """Downsampled series for Recharts: health proxy + oxygen + viability-like metrics."""
    series = {}
    for name, chip in lab.chips.items():
        series[name] = []
        for i, point in enumerate(chip.history[-80:]):
            row = {k: v for k, v in point.items() if k != "t"}
            oxy = row.get("oxygen", 95)
            via = row.get("viability", row.get("contractility", 90))
            row["health"] = round((oxy + via) / 2, 2)
            row["tick"] = i
            series[name].append(row)
    return series


@app.get("/api/experiments", response_model=list[ExperimentOut])
def experiments():
    db = SessionLocal()
    try:
        rows = db.scalars(select(Experiment).order_by(desc(Experiment.id)).limit(50)).all()
        return rows
    finally:
        db.close()


@app.get("/api/insights")
def insights():
    live_state = lab.live()
    lines = []
    for organ, pred in live_state.predictions.items():
        lines.extend(pred.insights)
    return {
        "headline": f"Panel health {live_state.mean_health}/100 with {live_state.toxicity_alerts} critical alerts.",
        "insights": lines[:18],
        "failure_watch": [
            {
                "organ": o.organ,
                "eta_min": o.failure_eta_min,
                "condition": o.condition,
            }
            for o in live_state.organs
            if o.failure_eta_min
        ],
    }


@app.get("/api/reports/experiment.pdf")
def experiment_pdf():
    data = build_experiment_pdf()
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=organtwin-experiment.pdf"},
    )


@app.get("/api/reports/fda.pdf")
def fda_pdf():
    data = build_fda_style_pdf()
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=organtwin-fda-safety.pdf"},
    )
