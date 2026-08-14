from __future__ import annotations

import csv
from pathlib import Path

from conftest import FakeProvider

from app.config import Settings
from app.models import ServiceStatus
from app.service import RAGService


async def test_service_builds_and_returns_server_owned_contexts(tmp_path: Path) -> None:
    dataset = tmp_path / "movies.csv"
    with dataset.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "title", "plot"])
        writer.writeheader()
        writer.writerows(
            [
                {
                    "source_id": "1",
                    "title": "2001: A Space Odyssey",
                    "plot": "HAL is the computer aboard the ship.",
                },
                {"source_id": "2", "title": "Jaws", "plot": "A shark attacks a town."},
            ]
        )
    settings = Settings(
        openai_api_key="test",
        dataset_path=dataset,
        embedding_cache_dir=tmp_path / "cache",
    )
    service = RAGService(settings, provider=FakeProvider())

    await service.build()
    response = await service.query("Which movie has the HAL computer?", top_k=1)

    assert service.status is ServiceStatus.READY
    assert service.indexed_movies == 2
    assert response.contexts[0].title == "2001: A Space Odyssey"
    assert response.contexts[0].snippet == "HAL is the computer aboard the ship."
