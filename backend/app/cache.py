from __future__ import annotations

import json
from pathlib import Path


class EmbeddingCache:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, fingerprint: str) -> Path:
        return self.directory / f"{fingerprint}.json"

    def load(self, fingerprint: str, expected_count: int) -> list[list[float]] | None:
        path = self._path(fingerprint)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        vectors = payload.get("embeddings")
        if payload.get("fingerprint") != fingerprint or not isinstance(vectors, list):
            return None
        if len(vectors) != expected_count:
            return None
        return vectors

    def save(self, fingerprint: str, embeddings: list[list[float]]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(fingerprint)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"fingerprint": fingerprint, "embeddings": embeddings}),
            encoding="utf-8",
        )
        temporary.replace(path)

