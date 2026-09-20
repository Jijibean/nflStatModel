import nflreadpy as nfl
import pandas as pd


def load_player_games(season: int) -> pd.DataFrame:
    return nfl.load_player_stats([season]).to_pandas()