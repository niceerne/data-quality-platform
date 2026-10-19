import pandas as pd

from dqp.quality import checks
from dqp.quality.runner import run_checks_for_table


def _customers():
    return pd.DataFrame({
        "customer_id": [1, 2, 2, 3],
        "email": ["a@x.com", None, "bad@mail", "c@x.com"],
        "age": [30, -1, 200, 40],
        "signup_date": ["2024-01-01", "2099-01-01", "2024-02-01", "2024-03-01"],
    })


def test_missing_detects_nulls():
    r = checks.check_missing(_customers(), "t", "email", max_rate=0.0)
    assert r["failed_rows"] == 1 and r["status"] == "FAIL"


def test_missing_respects_threshold():
    r = checks.check_missing(_customers(), "t", "email", max_rate=0.5)
    assert r["status"] == "PASS"


def test_duplicates():
    r = checks.check_duplicates(_customers(), "t", ["customer_id"])
    assert r["failed_rows"] == 1


def test_invalid_email():
    r = checks.check_invalid(_customers(), "t", "email", "email")
    assert r["failed_rows"] == 1  # "bad@mail" ; None ignoré (couvert par check_missing)


def test_invalid_range():
    r = checks.check_invalid(_customers(), "t", "age", "range", min=0, max=120)
    assert r["failed_rows"] == 2


def test_invalid_not_future():
    r = checks.check_invalid(_customers(), "t", "signup_date", "not_future")
    assert r["failed_rows"] == 1


def test_schema_drift():
    r = checks.check_schema(_customers(), "t", ["customer_id", "email", "phone"])
    assert r["status"] == "FAIL"
    assert "phone" in r["details"] and "age" in r["details"]


def test_runner_applies_rules():
    rules = {
        "expected_columns": ["customer_id", "email", "age", "signup_date"],
        "missing": [{"column": "email", "max_rate": 0.0}],
        "duplicates": [{"keys": ["customer_id"]}],
        "invalid": [{"column": "age", "rule": "range", "min": 0, "max": 120}],
    }
    res = run_checks_for_table(_customers(), "t", rules)
    assert len(res) == 4
    assert {r["check_name"] for r in res} == {"schema", "missing", "duplicates", "invalid_range"}
