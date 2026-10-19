from __future__ import annotations

import pandas as pd

from . import checks


def run_checks_for_table(df: pd.DataFrame, table: str, rules: dict) -> list[dict]:
    """Applique toutes les règles déclarées dans sources.yml à un DataFrame."""
    results = []
    if "expected_columns" in rules:
        results.append(checks.check_schema(df, table, rules["expected_columns"]))
    for r in rules.get("missing", []):
        results.append(checks.check_missing(df, table, r["column"], r.get("max_rate", 0.0)))
    for r in rules.get("duplicates", []):
        results.append(checks.check_duplicates(df, table, r["keys"]))
    for r in rules.get("invalid", []):
        kw = {k: v for k, v in r.items() if k not in ("column", "rule")}
        results.append(checks.check_invalid(df, table, r["column"], r["rule"], **kw))
    return results


def results_to_df(results: list[dict], run_id: str) -> pd.DataFrame:
    df = pd.DataFrame(results)
    df.insert(0, "run_id", run_id)
    return df
