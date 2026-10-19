import pandas as pd
import requests


def fetch_api(url: str, timeout: int = 30) -> pd.DataFrame:
    """Appelle une API REST renvoyant une liste JSON et l'aplatit en DataFrame."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        data = data.get("results") or data.get("data") or [data]
    return pd.json_normalize(data)
