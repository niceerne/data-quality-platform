"""Contrôles qualité sur DataFrame. Chaque fonction renvoie un dict résultat."""
from __future__ import annotations

import pandas as pd

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$"


def _result(table, check, column, failed, total, status=None, details=""):
    rate = failed / total if total else 0.0
    return {
        "table_name": table,
        "check_name": check,
        "column_name": column,
        "status": status or ("PASS" if failed == 0 else "FAIL"),
        "failed_rows": int(failed),
        "total_rows": int(total),
        "failure_rate": float(rate),
        "details": details,
    }


def check_missing(df: pd.DataFrame, table: str, column: str, max_rate: float = 0.0) -> dict:
    if column not in df.columns:
        return _result(table, "missing", column, 0, len(df), "FAIL", "colonne absente")
    mask = df[column].isna() | (df[column].astype(str).str.strip() == "")
    failed = int(mask.sum())
    rate = failed / len(df) if len(df) else 0.0
    status = "PASS" if rate <= max_rate else "FAIL"
    return _result(table, "missing", column, failed, len(df), status, f"seuil={max_rate}")


def check_duplicates(df: pd.DataFrame, table: str, keys: list[str]) -> dict:
    missing = [k for k in keys if k not in df.columns]
    if missing:
        return _result(table, "duplicates", ",".join(keys), 0, len(df), "FAIL", f"clés absentes: {missing}")
    failed = int(df.duplicated(subset=keys, keep="first").sum())
    return _result(table, "duplicates", ",".join(keys), failed, len(df))


def check_invalid(df: pd.DataFrame, table: str, column: str, rule: str, **kw) -> dict:
    if column not in df.columns:
        return _result(table, f"invalid_{rule}", column, 0, len(df), "FAIL", "colonne absente")
    s = df[column]
    present = s.notna()
    if rule == "email":
        bad = present & ~s.astype(str).str.match(EMAIL_REGEX)
    elif rule == "range":
        num = pd.to_numeric(s, errors="coerce")
        bad = present & (num.isna() | False)
        if kw.get("min") is not None:
            bad |= present & (num < kw["min"])
        if kw.get("max") is not None:
            bad |= present & (num > kw["max"])
    elif rule == "not_future":
        dates = pd.to_datetime(s, errors="coerce")
        bad = present & (dates.isna() | (dates > pd.Timestamp.now()))
    else:
        raise ValueError(f"Règle inconnue : {rule}")
    return _result(table, f"invalid_{rule}", column, int(bad.sum()), len(df))


def check_schema(df: pd.DataFrame, table: str, expected_columns: list[str]) -> dict:
    actual = set(df.columns)
    expected = set(expected_columns)
    missing, extra = sorted(expected - actual), sorted(actual - expected)
    failed = len(missing) + len(extra)
    details = f"manquantes={missing} en_trop={extra}" if failed else ""
    return _result(table, "schema", None, failed, len(expected), details=details)
