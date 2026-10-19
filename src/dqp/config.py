import os
from pathlib import Path

import yaml

BASE_DIR = Path(os.getenv("DQP_BASE_DIR", Path(__file__).resolve().parents[2]))


def load_config(path: str | None = None) -> dict:
    cfg_path = Path(path) if path else BASE_DIR / "config" / "sources.yml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def database_url() -> str:
    user = os.getenv("POSTGRES_USER", "dqp")
    pwd = os.getenv("POSTGRES_PASSWORD", "dqp_password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "dqp")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
