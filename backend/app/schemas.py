"""Pydantic request/response contracts for the OrganTwin API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DrugApplyRequest(BaseModel):
    organ: str = Field(description="liver | heart | kidney | lungs | all")
    drug: list[str]
    dose_mg: float = Field(gt=0, le=5000)
    duration_h: float = Field(gt=0, le=72)
    age_group: str = "18-64"
    experiment_name: str = "Hackathon Organ-Chip Assay"


class ExperimentOut(BaseModel):
    id: int
    name: str
    organ: str
    drug: str
    dose_mg: float
    duration_h: float
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SensorPoint(BaseModel):
    metric: str
    value: float
    unit: str


class OrganSnapshot(BaseModel):
    organ: str
    health_score: float
    stress_level: float
    survival_rate: float
    damage_percent: float
    condition: str
    sensors: dict[str, SensorPoint]
    drug: str
    dose_mg: float
    duration_h: float
    exposure_elapsed_h: float
    failure_eta_min: float | None = None


class AlertOut(BaseModel):
    id: int | None = None
    organ: str
    severity: str
    kind: str
    message: str
    created_at: datetime | None = None


class ToxicityOut(BaseModel):
    organ: str
    label: str
    confidence: float
    probabilities: dict[str, float]
    risk_level: str
    toxicity_probability: float
    anomaly_score: float
    is_anomaly: bool
    insights: list[str]


class LiveState(BaseModel):
    ticks: int
    organs: list[OrganSnapshot]
    alerts: list[AlertOut]
    predictions: dict[str, ToxicityOut]
    active_experiments: int
    toxicity_alerts: int
    mean_health: float


class HistorySeries(BaseModel):
    organ: str
    metric: str
    points: list[dict[str, Any]]
