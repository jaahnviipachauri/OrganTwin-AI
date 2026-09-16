"""
In-memory organ laboratory: ticks chips, persists snapshots, runs AI.

The lab is the single source of truth for live dashboard state.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..config import TICK_SECONDS
from ..database import SessionLocal
from ..models import Alert, Experiment, Prediction, SensorReading
from ..schemas import AlertOut, LiveState, OrganSnapshot, SensorPoint, ToxicityOut
from .anomaly import detect_anomalies
from .insights import build_insights
from .ml_engine import get_engine
from .organ_sim import DRUGS, ORGAN_UNITS, OrganChip


class OrganLab:
    def __init__(self) -> None:
        self.chips = {name: OrganChip(name) for name in ("liver", "heart", "kidney", "lungs")}
        self.ticks = 0
        self.latest_alerts: list[AlertOut] = []
        self.latest_predictions: dict[str, ToxicityOut] = {}
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    async def _loop(self) -> None:
        while True:
            await self.step()
            await asyncio.sleep(TICK_SECONDS)

    async def step(self) -> None:
        async with self._lock:
            self.ticks += 1
            dt_hours = TICK_SECONDS / 3600 * 90  # compressed experimental time
            engine = get_engine()
            db = SessionLocal()
            new_alerts: list[AlertOut] = []
            try:
                for chip in self.chips.values():
                    chip.tick(dt_hours)
                    self._persist_sensors(db, chip)
                    for raw in detect_anomalies(chip):
                        row = Alert(
                            organ=raw["organ"],
                            severity=raw["severity"],
                            kind=raw["kind"],
                            message=raw["message"],
                        )
                        db.add(row)
                        db.flush()
                        new_alerts.append(
                            AlertOut(
                                id=row.id,
                                organ=row.organ,
                                severity=row.severity,
                                kind=row.kind,
                                message=row.message,
                                created_at=datetime.now(timezone.utc),
                            )
                        )
                    pred = engine.predict(chip.feature_vector())
                    insights = build_insights(chip, pred)
                    tox = ToxicityOut(
                        organ=chip.organ,
                        insights=insights,
                        **pred,
                    )
                    self.latest_predictions[chip.organ] = tox
                    db.add(
                        Prediction(
                            organ=chip.organ,
                            label=pred["label"],
                            confidence=pred["confidence"],
                            severe_probability=pred["probabilities"].get("Severe Toxicity", 0),
                            risk_level=pred["risk_level"],
                            payload=json.dumps({**pred, "insights": insights}),
                        )
                    )
                db.commit()
            finally:
                db.close()
            if new_alerts:
                self.latest_alerts = (new_alerts + self.latest_alerts)[:40]

    def _persist_sensors(self, db: Session, chip: OrganChip) -> None:
        units = ORGAN_UNITS[chip.organ]
        for metric, value in chip.state.items():
            db.add(
                SensorReading(
                    organ=chip.organ,
                    metric=metric,
                    value=round(value, 3),
                    unit=units.get(metric, ""),
                )
            )

    def apply_drug(self, organ: str, drugs: list[str], dose_mg: float, duration_h: float, age_group: str, name: str) -> list[Experiment]:
        targets = list(self.chips) if organ == "all" else [organ]
        db = SessionLocal()
        created: list[Experiment] = []
        try:
            for key in targets:
                if key not in self.chips:
                    raise ValueError("Unknown organ")
                self.chips[key].apply_drug(drugs, dose_mg, duration_h, age_group)
                exp = Experiment(
                    name=name,
                    organ=key,
                    drug=" + ".join(drugs) if drugs else "None",
                    dose_mg=dose_mg,
                    duration_h=duration_h,
                    status="running",
                )
                db.add(exp)
                created.append(exp)
            db.commit()
            for exp in created:
                db.refresh(exp)
        finally:
            db.close()
        return created

    def snapshot(self, chip: OrganChip) -> OrganSnapshot:
        twin = chip.twin_metrics()
        units = ORGAN_UNITS[chip.organ]
        sensors = {
            metric: SensorPoint(metric=metric, value=round(value, 3), unit=units.get(metric, ""))
            for metric, value in chip.state.items()
        }
        return OrganSnapshot(
            organ=chip.organ,
            sensors=sensors,
            drug=chip.drug,
            dose_mg=chip.dose_mg,
            duration_h=chip.duration_h,
            exposure_elapsed_h=round(chip.exposure_elapsed_h, 3),
            **twin,
        )

    def live(self) -> LiveState:
        organs = [self.snapshot(c) for c in self.chips.values()]
        mean_health = round(sum(o.health_score for o in organs) / len(organs), 1)
        running = sum(1 for c in self.chips.values() if c.drug != "None")
        tox_alerts = sum(1 for a in self.latest_alerts if a.severity == "critical")
        return LiveState(
            ticks=self.ticks,
            organs=organs,
            alerts=self.latest_alerts[:12],
            predictions=self.latest_predictions,
            active_experiments=running,
            toxicity_alerts=tox_alerts,
            mean_health=mean_health,
        )

    def ranking(self) -> list[dict]:
        scores = []
        for key, meta in DRUGS.items():
            # Score using current chips if that drug is applied, else catalog toxicity
            applied = [c for c in self.chips.values() if key in getattr(c, "active_drugs", [])]
            if applied:
                health = sum(c.health_score() for c in applied) / len(applied)
                tox = round(100 - health, 1)
            else:
                tox = round(meta["toxicity"] * 100, 1)
            scores.append(
                {
                    "drug": key,
                    "display": meta["display"],
                    "toxicity_score": tox,
                    "safety_class": meta["class"],
                    "note": meta["note"],
                }
            )
        scores.sort(key=lambda x: x["toxicity_score"])
        return scores


lab = OrganLab()
