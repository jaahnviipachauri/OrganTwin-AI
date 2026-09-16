"""Random Forest toxicity inference + Isolation Forest anomaly scoring."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.train_model import FEATURE_COLUMNS, LABELS, encode_features, train_and_persist

from ..config import ARTIFACT_DIR


class ToxicityEngine:
    def __init__(self) -> None:
        self.clf = None
        self.iso = None
        self.scaler = None
        self.metadata: dict = {}
        self.ensure_trained()

    def ensure_trained(self) -> None:
        rf = ARTIFACT_DIR / "toxicity_rf.joblib"
        if not rf.exists():
            train_and_persist()
        self.clf = joblib.load(ARTIFACT_DIR / "toxicity_rf.joblib")
        self.iso = joblib.load(ARTIFACT_DIR / "anomaly_iforest.joblib")
        self.scaler = joblib.load(ARTIFACT_DIR / "scaler.joblib")
        meta_path = ARTIFACT_DIR / "metadata.json"
        self.metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    def predict(self, feature_row: dict) -> dict:
        df = pd.DataFrame(
            [
                {
                    **feature_row,
                    "label": "Normal",
                }
            ]
        )
        encoded = encode_features(df)
        x = encoded[FEATURE_COLUMNS].astype(float)
        xs = self.scaler.transform(x)
        proba = self.clf.predict_proba(xs)[0]
        idx = int(np.argmax(proba))
        label = LABELS[idx]
        mapping = {LABELS[i]: float(round(p, 4)) for i, p in enumerate(proba)}
        tox_prob = float(round(mapping.get("Mild Toxicity", 0) * 0.45 + mapping.get("Severe Toxicity", 0), 4))
        if label == "Severe Toxicity" or tox_prob >= 0.62:
            risk = "High"
        elif label == "Mild Toxicity" or tox_prob >= 0.28:
            risk = "Moderate"
        else:
            risk = "Low"
        iso_score = float(self.iso.decision_function(xs)[0])
        is_anomaly = int(self.iso.predict(xs)[0]) == -1
        return {
            "label": label,
            "confidence": float(round(proba[idx], 4)),
            "probabilities": mapping,
            "risk_level": risk,
            "toxicity_probability": tox_prob,
            "anomaly_score": round(iso_score, 4),
            "is_anomaly": is_anomaly,
        }


engine: ToxicityEngine | None = None


def get_engine() -> ToxicityEngine:
    global engine
    if engine is None:
        engine = ToxicityEngine()
    return engine
