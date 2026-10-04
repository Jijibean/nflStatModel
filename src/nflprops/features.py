from pathlib import Path

import pandas as pd

from nflprops.data import load_player_games

POSITIONS = ("WR", "TE")
WINDOW = 3

def build_player_games(season: int, data_root: Path = Path("data")) -> pd.DataFrame:
    df = load_player_games(season, data_root)

    df = df[(df["season_type"] == "REG") & (df["position"].isin(POSITIONS))]
    df = df.sort_values(["player_id", "week"]).reset_index(drop=True)

    grouped = df.groupby("player_id")

    for col in ("targets", "receiving_yards", "target_share"):
        df[f"{col}_lag{WINDOW}"] = (
            grouped[col].shift(1).groupby(df["player_id"]).rolling(WINDOW, min_periods=1).mean()
            .reset_index(level=0, drop=True)
        )

    df["games_played_prior"] = grouped.cumcount()

    return df