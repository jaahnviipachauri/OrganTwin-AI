"""Runtime configuration for the OrganTwin API."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
TICK_SECONDS = 2.5
HISTORY_LIMIT = 240
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
