import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import database_url


def get_engine(url: str | None = None) -> Engine:
    return create_engine(url or database_url(), pool_pre_ping=True)


def write_df(df: pd.DataFrame, target: str, engine: Engine) -> int:
    """Charge un DataFrame dans `schema.table` (remplace le contenu)."""
    schema, table = target.split(".", 1)
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    df.to_sql(table, engine, schema=schema, if_exists="replace", index=False)
    return len(df)


def read_table(target: str, engine: Engine) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {target}", engine)
