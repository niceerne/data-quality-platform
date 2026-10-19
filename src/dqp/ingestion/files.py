from pathlib import Path

import pandas as pd

from ..config import BASE_DIR


def read_file(path: str) -> pd.DataFrame:
    """Lit un CSV ou un Excel (.xlsx/.xls) en DataFrame."""
    p = Path(path)
    if not p.is_absolute():
        p = BASE_DIR / p
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(p)
    raise ValueError(f"Format non supporté : {suffix}")
