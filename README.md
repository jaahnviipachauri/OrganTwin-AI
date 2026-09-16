# OrganTwin AI – Organ-on-Chip Digital Monitoring Platform

Hackathon-ready web app that simulates **liver / heart / kidney organ-on-chip** perfusion, streams sensors, predicts **Normal / Mild / Severe** toxicity with a scikit-learn Random Forest, flags anomalies, and exports PDF experiment + FDA-style safety reports.

The product story: pharmaceutical teams can **triage acute tox on digital twins** before spending animals on sentinel studies.

---

## 1. Folder structure

```
organ-twin-ai/
├── README.md                          # This file (setup + architecture)
├── DEPLOYMENT.md                      # Docker / production notes
├── docker-compose.yml
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app.db                         # Created at runtime (SQLite)
│   ├── data/
│   │   ├── sample_training.csv        # Hand-authored example labels
│   │   ├── sample_sensors.csv         # Example sensor dump
│   │   └── generated_training.csv     # Written when the model trains
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── train_model.py             # Synthetic data + RF + IsolationForest
│   │   └── artifacts/                 # joblib models (created on first run)
│   └── app/
│       ├── main.py                    # FastAPI routes
│       ├── config.py                  # Paths, tick rate, CORS
│       ├── database.py                # SQLAlchemy + SQLite
│       ├── models.py                  # Experiment, SensorReading, Alert, Prediction
│       ├── schemas.py                 # Pydantic contracts
│       └── services/
│           ├── organ_sim.py           # Chip physiology + drug PK-ish insult
│           ├── lab.py                 # Tick loop, persistence, ranking
│           ├── ml_engine.py           # Load/train models, infer
│           ├── anomaly.py             # O2 drop, pH, cell death rules
│           ├── insights.py            # Narrative AI recommendations
│           └── reports.py             # ReportLab PDFs
└── frontend/
    ├── package.json
    ├── app/                           # Next.js App Router pages
    ├── components/                    # Shell, cards, UI
    └── lib/                           # API client + live poll hook
```

### What each important file does

| File | Role |
| --- | --- |
| `backend/app/main.py` | HTTP API listed below. Starts the lab tick on process boot. |
| `backend/app/services/organ_sim.py` | Three organ state machines; Drug A/B/C shift sensors. |
| `backend/ml/train_model.py` | Builds ~2400 labeled traces, trains RF + IsolationForest. |
| `backend/app/services/ml_engine.py` | Feature encoding + class probabilities + risk. |
| `backend/app/services/anomaly.py` | Real-time hypoxia / pH / viability alerts. |
| `frontend/app/page.tsx` | Command-center dashboard. |
| `frontend/app/drug-lab/page.tsx` | Dose / duration / organ selector. |
| `frontend/app/analytics/page.tsx` | Recharts history and response curves. |
| `frontend/lib/useLive.ts` | Polls `/api/live` every 2.5s. |

---

## 2. API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/api/live` | Full dashboard snapshot |
| GET | `/api/organs` | All twins |
| GET | `/api/organs/{liver\|heart\|kidney}` | One twin |
| GET | `/api/compare` | Side-by-side twins + predictions |
| GET | `/api/drugs` | Drug A/B/C catalog |
| POST | `/api/drugs/apply` | `{ organ, drug, dose_mg, duration_h, experiment_name }` |
| GET | `/api/drugs/ranking` | Toxicity ranking |
| GET | `/api/predictions` | Latest RF calls |
| GET | `/api/alerts` | Persisted anomalies |
| GET | `/api/analytics/history` | SQLite sensor log |
| GET | `/api/analytics/trends` | In-memory chart series |
| GET | `/api/experiments` | Exposure runs |
| GET | `/api/insights` | Research bullets + failure ETA |
| GET | `/api/reports/experiment.pdf` | Download experiment PDF |
| GET | `/api/reports/fda.pdf` | Simulated FDA-style PDF |

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 3. Local setup

Requires **Python 3.11+** (3.13 works) and **Node 20+**.

```bash
cd organ-twin-ai

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional: train models ahead of time (also auto-runs on first API boot)
python -m ml.train_model
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Demo path:

1. Dashboard should show three healthy chips.
2. **Drug simulator** → Drug C, high dose, all organs → Start perfusion.
3. Watch oxygen/viability fall, alerts fire, AI labels move to Mild/Severe.
4. **Analytics** for curves; **Reports** for PDFs.

---

## 4. AI / ML

- **RandomForestClassifier** maps dose, duration, organ one-hots, and physiology to `Normal | Mild Toxicity | Severe Toxicity`.
- **IsolationForest** flags out-of-distribution sensor vectors.
- Rule-based detectors catch sudden O₂ drops, pH excursions, and cell-death events so the demo is reliable even if the forest is uncertain.
- Failure-ahead ETA uses viability/oxygen slope while a toxic drug is on-chip.

This is a **demonstration model** on synthetic OoC-like data, not a validated diagnostic.

---

## 5. Stack

Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS, Recharts  
Backend: FastAPI, SQLAlchemy, SQLite  
ML: scikit-learn, joblib, pandas, numpy  
PDF: ReportLab
