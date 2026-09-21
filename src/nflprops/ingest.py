import json
from datetime import datetime, timezone
from pathlib import Path

import nflreadpy as nfl
import pandas as pd

LOADERS = {
    "player_stats": nfl.load_player_stats,
}

def snapshot(dataset: str, seasons: list[int], data_root: Path) -> Path:
    if dataset not in LOADERS:
        raise ValueError(f"Unknown dataset: {dataset}")
    loader = LOADERS[dataset]
    df = loader(seasons).to_pandas()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    output_dir = data_root / "raw" / dataset / f"fetched_at={stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = output_dir / "data.parquet"
    df.to_parquet(data_path, index=False)
    manifest = {
        "dataset": dataset,
        "seasons": seasons,
        "fetched_at_utc": stamp,
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": list(df.columns),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return output_dir

def read_snapshot(dataset: str, data_root: Path, fetched_at: str | None = None) -> pd.DataFrame:
    if fetched_at is None:
        # Find the latest snapshot
        dataset_dir = data_root / "raw" / dataset
        snapshots = sorted(dataset_dir.glob("fetched_at=*"), reverse=True)
        if not snapshots:
            raise FileNotFoundError(f"No snapshots found for dataset: {dataset}")
        snapshot_dir = snapshots[0]
    else:
        snapshot_dir = data_root / "raw" / dataset / f"fetched_at={fetched_at}"
        if not snapshot_dir.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_dir}")
    data_path = snapshot_dir / "data.parquet"
    return pd.read_parquet(data_path)