from __future__ import annotations

from pathlib import Path

from app.cache import EmbeddingCache


def test_embedding_cache_round_trip_and_count_guard(tmp_path: Path) -> None:
    cache = EmbeddingCache(tmp_path)
    vectors = [[1.0, 0.0], [0.0, 1.0]]

    cache.save("fingerprint", vectors)

    assert cache.load("fingerprint", expected_count=2) == vectors
    assert cache.load("fingerprint", expected_count=3) is None
    assert cache.load("different", expected_count=2) is None

