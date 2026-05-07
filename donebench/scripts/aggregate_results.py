from __future__ import annotations

import json
from pathlib import Path

from donebench.core.metrics import aggregate_results


def load_results(root: Path) -> list[dict]:
    rows = []
    for path in sorted(root.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def aggregate(root: Path) -> dict:
    rows = load_results(root)
    tables = aggregate_results(rows)
    for name, df in tables.items():
        df.to_csv(root / f"{name}.csv", index=False)
    return {name: len(df) for name, df in tables.items()}
