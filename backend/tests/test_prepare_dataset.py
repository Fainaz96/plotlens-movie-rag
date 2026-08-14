from __future__ import annotations

import csv
from pathlib import Path

from scripts.prepare_dataset import prepare


def test_prepare_filters_blanks_deduplicates_and_is_reproducible(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    fieldnames = ["Title", "Plot"]
    rows = [
        {"Title": "2001: A Space Odyssey", "Plot": "HAL controls the ship."},
        {"Title": "Duplicate", "Plot": "Same plot"},
        {"Title": "Duplicate", "Plot": "Same plot"},
        {"Title": "", "Plot": "Missing title"},
        {"Title": "Missing plot", "Plot": ""},
        *({"Title": f"Movie {index}", "Plot": f"Plot {index}"} for index in range(20)),
    ]
    with source.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    prepare(source, first, size=10, seed=42)
    prepare(source, second, size=10, seed=42)

    assert first.read_bytes() == second.read_bytes()
    with first.open(encoding="utf-8", newline="") as stream:
        prepared = list(csv.DictReader(stream))
    assert len(prepared) == 10
    assert sum(row["title"] == "Duplicate" for row in prepared) <= 1
    assert any(row["title"] == "2001: A Space Odyssey" for row in prepared)

