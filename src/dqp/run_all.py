"""Pipeline complet : ingestion -> raw, puis contrôles qualité -> dq.check_results.

Usage : PYTHONPATH=src python -m dqp.run_all
Étapes aussi appelables séparément par Airflow (ingest / run_quality).
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import text

from .config import load_config
from .db import get_engine, read_table, write_df
from .ingestion import fetch_api, read_file, read_query
from .quality import results_to_df, run_checks_for_table


def ingest(engine=None) -> dict[str, int]:
    cfg = load_config()["sources"]
    engine = engine or get_engine()
    loaded: dict[str, int] = {}

    for src in cfg.get("files", []):
        loaded[src["target_table"]] = write_df(read_file(src["path"]), src["target_table"], engine)

    for src in cfg.get("api", []):
        url = os.getenv(src["url_env"])
        if url:
            loaded[src["target_table"]] = write_df(fetch_api(url), src["target_table"], engine)

    for src in cfg.get("database", []):
        url = os.getenv(src["url_env"])
        if url:
            loaded[src["target_table"]] = write_df(read_query(url, src["query"]), src["target_table"], engine)

    return loaded


def run_quality(run_id: str | None = None, engine=None) -> str:
    run_id = run_id or datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
    engine = engine or get_engine()
    rules_by_table = load_config()["quality"]

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO dq.run_log (run_id, status) VALUES (:r, 'RUNNING')"), {"r": run_id})

    all_results = []
    for table, rules in rules_by_table.items():
        df = read_table(table, engine)
        all_results.extend(run_checks_for_table(df, table, rules))

    results_to_df(all_results, run_id).to_sql(
        "check_results", engine, schema="dq", if_exists="append", index=False
    )

    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE dq.run_log SET finished_at = now(), status = :s WHERE run_id = :r"),
            {"s": "FAILED_CHECKS" if failed else "OK", "r": run_id},
        )
    print(f"[{run_id}] {len(all_results)} contrôles, {failed} en échec")
    return run_id


def main() -> None:
    load_dotenv()
    print("Ingestion :", ingest())
    run_quality()


if __name__ == "__main__":
    main()
