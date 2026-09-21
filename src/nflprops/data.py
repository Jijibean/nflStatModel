from pathlib import Path

import pandas as pd
import pytest

from nflprops.ingest import read_snapshot


def load_player_games(season: int, data_root: Path = Path("data")) -> pd.DataFrame:
    df = read_snapshot("player_stats", data_root)
    df = df[df["season"] == season]
    if df.empty:
        raise ValueError(f"Latest player_stats snapshot contains no rows for season {season}")
    return df