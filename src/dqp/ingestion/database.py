import pandas as pd
from sqlalchemy import create_engine


def read_query(url: str, query: str) -> pd.DataFrame:
    """Exécute une requête sur une base source externe."""
    engine = create_engine(url)
    try:
        return pd.read_sql(query, engine)
    finally:
        engine.dispose()
