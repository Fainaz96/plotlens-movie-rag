from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models import HealthResponse, QueryRequest, QueryResponse, ServiceStatus
from app.provider import ProviderError
from app.service import RAGService

LOGGER = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, service: RAGService | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    rag_service = service or RAGService(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.rag_service = rag_service

        async def initialize() -> None:
            try:
                await rag_service.build()
            except Exception:
                LOGGER.exception("RAG index initialization failed")

        task = asyncio.create_task(initialize())
        yield
        if not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(
        title="PlotLens API",
        summary="Grounded answers over a compact Wikipedia movie-plot index.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.rag_service = rag_service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health", response_model=HealthResponse, tags=["operations"])
    async def health(request: Request) -> HealthResponse:
        return request.app.state.rag_service.health()

    @app.post("/api/v1/query", response_model=QueryResponse, tags=["rag"])
    async def query(payload: QueryRequest, request: Request) -> QueryResponse:
        current_service: RAGService = request.app.state.rag_service
        if current_service.status is not ServiceStatus.READY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The movie index is not ready. Check /health and try again shortly.",
            )
        try:
            return await current_service.query(payload.query, payload.top_k)
        except ProviderError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    return app


app = create_app()

