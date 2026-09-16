"""
Train OrganTwin AI models from synthetic organ-on-chip data.

Outputs (written to backend/ml/artifacts/):
  - toxicity_rf.joblib       Random Forest classifier (Normal / Mild / Severe)
  - anomaly_iforest.joblib   Isolation Forest for sensor outliers
  - scaler.joblib            Shared StandardScaler for numeric features
  - metadata.json            Feature names, class labels, training stats

Run from the backend/ directory:
  python -m ml.train_model
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
FEATURE_COLUMNS = [
    "dose_mg",
    "duration_h",
    "oxygen",
    "ph",
    "viability",
    "lactate",
    "toxic_metabolites",
    "heartbeat",
    "contractility",
    "filtration",
    "glucose",
    "organ_heart",
    "organ_kidney",
    "organ_liver",
    "organ_lungs",
]
LABELS = ["Normal", "Mild Toxicity", "Severe Toxicity"]


def _clip(value: float, lo: float, hi: float) -> float:
    return float(np.clip(value, lo, hi))


def synthesize_dataset(n: int = 2400, seed: int = 42) -> pd.DataFrame:
    """Generate labeled organ-chip traces that mimic safe vs toxic drug exposure."""
    rng = np.random.default_rng(seed)
    organs = np.array(["liver", "heart", "kidney", "lungs"])
    drugs = np.array(["Drug A", "Drug B", "Drug C"])
    rows: list[dict] = []

    for _ in range(n):
        organ = rng.choice(organs)
        drug = rng.choice(drugs, p=[0.38, 0.34, 0.28])
        dose = float(rng.uniform(2, 60))
        duration = float(rng.uniform(1, 36))

        # Baseline healthy chip physiology
        oxygen = rng.normal(97.0, 1.2)
        ph = rng.normal(7.40, 0.02)
        viability = rng.normal(98.0, 1.0)
        lactate = rng.normal(0.9, 0.15)
        metabolites = rng.normal(1.2, 0.3)
        heartbeat = rng.normal(72, 4)
        contractility = rng.normal(92, 3)
        filtration = rng.normal(108, 6)
        glucose = rng.normal(95, 5)

        stress = (dose / 40.0) * (duration / 18.0)
        if drug == "Drug B":
            oxygen -= 12 * stress
            ph -= 0.18 * stress
            viability -= 18 * stress
            lactate += 2.2 * stress
            metabolites += 9 * stress
            heartbeat += 14 * stress
            contractility -= 16 * stress
            filtration -= 22 * stress
            glucose -= 12 * stress
        elif drug == "Drug C":
            oxygen -= 28 * stress
            ph -= 0.38 * stress
            viability -= 42 * stress
            lactate += 5.4 * stress
            metabolites += 22 * stress
            heartbeat += 28 * stress if stress < 1.2 else -20 * stress
            contractility -= 38 * stress
            filtration -= 48 * stress
            glucose -= 28 * stress

        oxygen = _clip(oxygen + rng.normal(0, 1.4), 20, 100)
        ph = _clip(ph + rng.normal(0, 0.03), 6.6, 7.7)
        viability = _clip(viability + rng.normal(0, 2.0), 5, 100)
        lactate = _clip(lactate + abs(rng.normal(0, 0.2)), 0.2, 12)
        metabolites = _clip(metabolites + abs(rng.normal(0, 0.4)), 0.1, 60)
        heartbeat = _clip(heartbeat + rng.normal(0, 3), 20, 180)
        contractility = _clip(contractility + rng.normal(0, 2), 8, 100)
        filtration = _clip(filtration + rng.normal(0, 4), 8, 140)
        glucose = _clip(glucose + rng.normal(0, 3), 20, 160)

        # Rule-based labels that the forest should recover from physiology
        if viability < 55 or oxygen < 60 or ph < 7.05 or metabolites > 22:
            label = "Severe Toxicity"
        elif viability < 82 or oxygen < 86 or ph < 7.25 or metabolites > 8:
            label = "Mild Toxicity"
        else:
            label = "Normal"

        rows.append(
            {
                "organ": organ,
                "drug": drug,
                "dose_mg": round(dose, 2),
                "duration_h": round(duration, 2),
                "oxygen": round(oxygen, 2),
                "ph": round(ph, 3),
                "viability": round(viability, 2),
                "lactate": round(lactate, 2),
                "toxic_metabolites": round(metabolites, 2),
                "heartbeat": round(heartbeat, 2),
                "contractility": round(contractility, 2),
                "filtration": round(filtration, 2),
                "glucose": round(glucose, 2),
                "label": label,
            }
        )

    return pd.DataFrame(rows)


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    encoded = df.copy()
    dummies = pd.get_dummies(encoded["organ"], prefix="organ")
    for col in ["organ_heart", "organ_kidney", "organ_liver", "organ_lungs"]:
        if col not in dummies.columns:
            dummies[col] = 0
    encoded = pd.concat([encoded, dummies[["organ_heart", "organ_kidney", "organ_liver", "organ_lungs"]]], axis=1)
    return encoded


def train_and_persist() -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    df = synthesize_dataset()
    sample_path = Path(__file__).resolve().parent.parent / "data" / "generated_training.csv"
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(sample_path, index=False)

    encoded = encode_features(df)
    x = encoded[FEATURE_COLUMNS].astype(float)
    y = encoded["label"].map({name: i for i, name in enumerate(LABELS)})

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=7, stratify=y
    )
    scaler = StandardScaler()
    x_train_s = scaler.fit_transform(x_train)
    x_test_s = scaler.transform(x_test)

    clf = RandomForestClassifier(
        n_estimators=220,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=7,
        n_jobs=-1,
    )
    clf.fit(x_train_s, y_train)
    report = classification_report(y_test, clf.predict(x_test_s), target_names=LABELS, output_dict=True)

    iso = IsolationForest(contamination=0.08, random_state=7)
    iso.fit(x_train_s)

    joblib.dump(clf, ARTIFACT_DIR / "toxicity_rf.joblib")
    joblib.dump(iso, ARTIFACT_DIR / "anomaly_iforest.joblib")
    joblib.dump(scaler, ARTIFACT_DIR / "scaler.joblib")
    metadata = {
        "feature_columns": FEATURE_COLUMNS,
        "labels": LABELS,
        "accuracy": report["accuracy"],
        "report": report,
        "n_samples": int(len(df)),
    }
    (ARTIFACT_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Trained Random Forest accuracy: {report['accuracy']:.3f}")
    print(f"Artifacts written to {ARTIFACT_DIR}")
    return metadata


if __name__ == "__main__":
    train_and_persist()
