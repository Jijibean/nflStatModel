from pathlib import Path

import polars as pl
import pytest

from nflprops.ingest import LOADERS, read_snapshot, snapshot


def fake_loader(seasons: list[int]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "season": [2025, 2025, 2025],
            "week": [1, 2, 3],
            "player_id": ["00-0000001", "00-0000001", "00-0000002"],
            "receiving_yards": [40, 75, 12],
        }
    )


@pytest.fixture
def patched_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(LOADERS, "player_stats", fake_loader)


def test_manifest_matches_data(tmp_path: Path, patched_loader: None) -> None:
    import json

    import pandas as pd

    out = snapshot("player_stats", [2025], tmp_path)
    df = pd.read_parquet(out / "data.parquet")
    manifest = json.loads((out / "manifest.json").read_text())

    assert manifest["n_rows"] == len(df)
    assert manifest["n_cols"] == df.shape[1]
    assert manifest["columns"] == list(df.columns)
    assert manifest["dataset"] == "player_stats"
    assert manifest["seasons"] == [2025]


def test_round_trip(tmp_path: Path, patched_loader: None) -> None:
    snapshot("player_stats", [2025], tmp_path)
    df = read_snapshot("player_stats", tmp_path)

    assert len(df) == 3
    assert list(df.columns) == ["season", "week", "player_id", "receiving_yards"]


def test_unknown_dataset_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        snapshot("not_a_dataset", [2025], tmp_path)


def test_read_with_no_snapshots_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_snapshot("player_stats", tmp_path)


def test_two_snapshots_stay_distinct(tmp_path: Path, patched_loader: None) -> None:
    first = snapshot("player_stats", [2025], tmp_path)
    second = snapshot("player_stats", [2025], tmp_path)

    assert first != second
    assert first.exists()
    assert second.exists()