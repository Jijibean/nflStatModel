from pathlib import Path

import pytest

from nflprops.data import load_player_games


def test_package_imports() -> None:
    import nflprops

    assert nflprops is not None

PLAYER_ID = "00-0036322" 
SEASON, WEEK = 2025, 3
EXPECTED_RECEIVING_YARDS = 75


def test_receiving_yards_matches_ground_truth() -> None:
    if not Path("data/raw/player_stats").exists():
        pytest.skip("no player_stats snapshot; run snapshot() first")
    df = load_player_games(SEASON)
    row = df[(df.player_id == PLAYER_ID)
             & (df.week == WEEK)
             & (df.season_type == "REG")]
    assert len(row) == 1
    assert row.receiving_yards.iloc[0] == EXPECTED_RECEIVING_YARDS