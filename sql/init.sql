CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dq;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS dq.run_log (
    run_id        TEXT PRIMARY KEY,
    started_at    TIMESTAMP NOT NULL DEFAULT now(),
    finished_at   TIMESTAMP,
    status        TEXT
);

CREATE TABLE IF NOT EXISTS dq.check_results (
    id            SERIAL PRIMARY KEY,
    run_id        TEXT NOT NULL,
    checked_at    TIMESTAMP NOT NULL DEFAULT now(),
    table_name    TEXT NOT NULL,
    check_name    TEXT NOT NULL,
    column_name   TEXT,
    status        TEXT NOT NULL,          -- PASS / WARN / FAIL
    failed_rows   INTEGER NOT NULL DEFAULT 0,
    total_rows    INTEGER NOT NULL DEFAULT 0,
    failure_rate  DOUBLE PRECISION NOT NULL DEFAULT 0,
    details       TEXT
);
