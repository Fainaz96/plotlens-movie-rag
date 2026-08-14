from __future__ import annotations

import argparse
import csv
import random
import re
from pathlib import Path

ANCHOR_TITLES = (
    "2001: A Space Odyssey",
    "The Matrix",
    "Titanic",
    "The Godfather",
    "Toy Story",
    "Psycho",
    "Alien",
    "Jaws",
    "The Terminator",
    "Back to the Future",
)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def prepare(source: Path, output: Path, size: int = 300, seed: int = 42) -> None:
    with source.open(encoding="utf-8", newline="") as stream:
        source_rows = list(csv.DictReader(stream))

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(source_rows):
        title = clean(row.get("Title"))
        plot = clean(row.get("Plot"))
        key = (title.casefold(), plot.casefold())
        if not title or not plot or key in seen:
            continue
        seen.add(key)
        unique.append({"source_id": f"wiki-{index:05d}", "title": title, "plot": plot})

    anchors: list[dict[str, str]] = []
    anchor_keys: set[str] = set()
    for title in ANCHOR_TITLES:
        match = next((row for row in unique if row["title"].casefold() == title.casefold()), None)
        if match is not None:
            anchors.append(match)
            anchor_keys.add(match["source_id"])

    candidates = [row for row in unique if row["source_id"] not in anchor_keys]
    if len(candidates) + len(anchors) < size:
        raise ValueError(f"Only {len(candidates) + len(anchors)} valid unique movies are available.")
    selected = anchors + random.Random(seed).sample(candidates, size - len(anchors))
    selected.sort(key=lambda row: row["source_id"])

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "title", "plot"])
        writer.writeheader()
        writer.writerows(selected)

    included = ", ".join(row["title"] for row in anchors)
    print(f"Wrote {len(selected)} movies to {output}")
    print(f"Included anchor titles: {included}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the reproducible PlotLens dataset subset.")
    parser.add_argument("source", type=Path, help="Path to wiki_movie_plots_deduped.csv")
    parser.add_argument("--output", type=Path, default=Path("data/movies.csv"))
    parser.add_argument("--size", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    prepare(args.source, args.output, size=args.size, seed=args.seed)


if __name__ == "__main__":
    main()

