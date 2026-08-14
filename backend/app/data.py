from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from app.models import MovieRow, PlotChunk


def load_movies(path: Path) -> list[MovieRow]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = [MovieRow.model_validate(row) for row in csv.DictReader(stream)]
    if not rows:
        raise ValueError("The movie dataset is empty.")
    return rows


def chunk_words(text: str, size: int = 300, overlap: int = 50) -> list[str]:
    if size <= 0:
        raise ValueError("Chunk size must be positive.")
    if overlap < 0 or overlap >= size:
        raise ValueError("Chunk overlap must be non-negative and smaller than chunk size.")

    words = text.split()
    if not words:
        return []

    step = size - overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        chunk = words[start : start + size]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if start + size >= len(words):
            break
    return chunks


def make_chunk_id(movie: MovieRow, chunk_index: int, text: str) -> str:
    payload = f"{movie.source_id}\n{movie.title}\n{chunk_index}\n{text}".encode()
    return hashlib.sha256(payload).hexdigest()[:20]


def chunk_movies(movies: list[MovieRow], size: int = 300, overlap: int = 50) -> list[PlotChunk]:
    chunks: list[PlotChunk] = []
    for movie in movies:
        for index, text in enumerate(chunk_words(movie.plot, size=size, overlap=overlap)):
            chunks.append(
                PlotChunk(
                    chunk_id=make_chunk_id(movie, index, text),
                    source_id=movie.source_id,
                    title=movie.title,
                    chunk_index=index,
                    text=text,
                )
            )
    return chunks


def dataset_fingerprint(
    path: Path,
    *,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int,
) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    digest.update(f"\n{embedding_model}\n{chunk_size}\n{chunk_overlap}".encode())
    return digest.hexdigest()

