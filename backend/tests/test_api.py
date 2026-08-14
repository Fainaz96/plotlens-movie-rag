from __future__ import annotations

import httpx

from app.config import Settings
from app.main import create_app
from app.models import (
    HealthResponse,
    QueryResponse,
    RetrievedContext,
    ServiceStatus,
)
from app.provider import ProviderError


class StubService:
    def __init__(self, status: ServiceStatus = ServiceStatus.READY) -> None:
        self.status = status

    async def build(self) -> None:
        return None

    def health(self) -> HealthResponse:
        return HealthResponse(
            status=self.status,
            indexed_movies=300 if self.status is ServiceStatus.READY else 0,
            indexed_chunks=410 if self.status is ServiceStatus.READY else 0,
            chat_model="chat-test",
            embedding_model="embedding-test",
        )

    async def query(self, query: str, top_k: int) -> QueryResponse:
        return QueryResponse(
            answer="The movie is 2001: A Space Odyssey.",
            contexts=[
                RetrievedContext(
                    title="2001: A Space Odyssey",
                    snippet="HAL controls the ship.",
                    score=0.91,
                    chunk_id="chunk-1",
                )
            ],
            reasoning="The retrieved plot explicitly identifies HAL.",
        )


class FailingService(StubService):
    async def query(self, query: str, top_k: int) -> QueryResponse:
        raise ProviderError("The AI provider could not generate an answer.")


def make_client(service: StubService) -> httpx.AsyncClient:
    settings = Settings(
        openai_api_key="super-secret-key",
        frontend_origin="http://localhost:3100",
    )
    app = create_app(settings=settings, service=service)  # type: ignore[arg-type]
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_query_contract() -> None:
    async with make_client(StubService()) as client:
        response = await client.post(
            "/api/v1/query",
            json={"query": "Which movie features HAL?", "top_k": 5},
        )

    assert response.status_code == 200
    assert set(response.json()) == {"answer", "contexts", "reasoning"}
    assert response.json()["contexts"][0]["title"] == "2001: A Space Odyssey"


async def test_validation_rejects_blank_short_and_invalid_top_k() -> None:
    async with make_client(StubService()) as client:
        blank = await client.post("/api/v1/query", json={"query": "   ", "top_k": 5})
        too_large = await client.post("/api/v1/query", json={"query": "valid", "top_k": 9})

    assert blank.status_code == 422
    assert too_large.status_code == 422


async def test_query_returns_503_until_ready() -> None:
    async with make_client(StubService(ServiceStatus.INITIALIZING)) as client:
        response = await client.post("/api/v1/query", json={"query": "Which movie?"})

    assert response.status_code == 503
    assert "not ready" in response.json()["detail"]


async def test_provider_failure_returns_safe_502() -> None:
    async with make_client(FailingService()) as client:
        response = await client.post("/api/v1/query", json={"query": "Which movie?"})

    assert response.status_code == 502
    assert response.json()["detail"] == "The AI provider could not generate an answer."


async def test_health_does_not_expose_api_key() -> None:
    async with make_client(StubService()) as client:
        response = await client.get("/health")

    body = response.text
    assert response.status_code == 200
    assert "super-secret-key" not in body
    assert response.json()["indexed_movies"] == 300
