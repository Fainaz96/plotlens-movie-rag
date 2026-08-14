from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.data import chunk_movies, chunk_words, dataset_fingerprint
from app.models import MovieRow


def test_chunk_words_uses_overlap_without_losing_words() -> None:
    words = [f"word-{index}" for index in range(650)]

    chunks = chunk_words(" ".join(words), size=300, overlap=50)

    assert [len(chunk.split()) for chunk in chunks] == [300, 300, 150]
    assert chunks[0].split()[-50:] == chunks[1].split()[:50]
    assert chunks[1].split()[-50:] == chunks[2].split()[:50]


@pytest.mark.parametrize("size,overlap", [(0, 0), (100, -1), (100, 100), (100, 101)])
def test_chunk_words_rejects_invalid_parameters(size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk_words("some words", size=size, overlap=overlap)


def test_chunk_ids_are_stable_and_metadata_is_preserved() -> None:
    movie = MovieRow(source_id="wiki-1", title="Example", plot="one two three four")

    first = chunk_movies([movie], size=3, overlap=1)
    second = chunk_movies([movie], size=3, overlap=1)

    assert first == second
    assert first[0].source_id == "wiki-1"
    assert first[0].title == "Example"
    assert first[0].chunk_index == 0
    assert first[0].chunk_id != first[1].chunk_id


def test_dataset_fingerprint_changes_with_data_or_embedding_contract(tmp_path: Path) -> None:
    dataset = tmp_path / "movies.csv"
    with dataset.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "title", "plot"])
        writer.writeheader()
        writer.writerow({"source_id": "1", "title": "A", "plot": "Plot A"})

    baseline = dataset_fingerprint(
        dataset,
        embedding_model="embedding-a",
        chunk_size=300,
        chunk_overlap=50,
    )
    changed_model = dataset_fingerprint(
        dataset,
        embedding_model="embedding-b",
        chunk_size=300,
        chunk_overlap=50,
    )
    dataset.write_text(dataset.read_text(encoding="utf-8") + "2,B,Plot B\n", encoding="utf-8")
    changed_data = dataset_fingerprint(
        dataset,
        embedding_model="embedding-a",
        chunk_size=300,
        chunk_overlap=50,
    )

    assert baseline != changed_model
    assert baseline != changed_data

