from __future__ import annotations

import asyncio
from collections.abc import Callable

from app.cache import EmbeddingCache
from app.config import Settings
from app.data import chunk_movies, dataset_fingerprint, load_movies
from app.models import (
    HealthResponse,
    QueryResponse,
    RetrievedContext,
    ServiceStatus,
)
from app.provider import AIProvider, OpenAIProvider
from app.retriever import ChromaRetriever

RetrieverFactory = Callable[[], ChromaRetriever]


class RAGService:
    def __init__(
        self,
        settings: Settings,
        provider: AIProvider | None = None,
        retriever_factory: RetrieverFactory = ChromaRetriever,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.retriever_factory = retriever_factory
        self.retriever: ChromaRetriever | None = None
        self.status = ServiceStatus.INITIALIZING
        self.indexed_movies = 0
        self.indexed_chunks = 0
        self.message: str | None = None

    async def build(self) -> None:
        self.status = ServiceStatus.INITIALIZING
        self.message = None
        try:
            if self.provider is None:
                if not self.settings.openai_api_key:
                    raise ValueError("OPENAI_API_KEY is not configured.")
                self.provider = OpenAIProvider(
                    api_key=self.settings.openai_api_key,
                    chat_model=self.settings.openai_chat_model,
                    embedding_model=self.settings.openai_embedding_model,
                    timeout_seconds=self.settings.openai_timeout_seconds,
                    batch_size=self.settings.embedding_batch_size,
                )

            movies = load_movies(self.settings.dataset_path)
            chunks = chunk_movies(
                movies,
                size=self.settings.chunk_size_words,
                overlap=self.settings.chunk_overlap_words,
            )
            fingerprint = dataset_fingerprint(
                self.settings.dataset_path,
                embedding_model=self.settings.openai_embedding_model,
                chunk_size=self.settings.chunk_size_words,
                chunk_overlap=self.settings.chunk_overlap_words,
            )
            cache = EmbeddingCache(self.settings.embedding_cache_dir)
            embeddings = cache.load(fingerprint, expected_count=len(chunks))
            if embeddings is None:
                embeddings = await self.provider.embed([chunk.text for chunk in chunks])
                cache.save(fingerprint, embeddings)

            retriever = self.retriever_factory()
            await asyncio.to_thread(retriever.add, chunks, embeddings)
            self.retriever = retriever
            self.indexed_movies = len(movies)
            self.indexed_chunks = len(chunks)
            self.status = ServiceStatus.READY
        except Exception:
            self.status = ServiceStatus.FAILED
            self.message = (
                "Index initialization failed. Check the dataset, OpenAI configuration, and logs."
            )
            raise

    async def query(self, query: str, top_k: int) -> QueryResponse:
        if self.status is not ServiceStatus.READY or self.retriever is None:
            raise RuntimeError("The movie index is not ready.")
        assert self.provider is not None
        query_vectors = await self.provider.embed([query])
        matches = await asyncio.to_thread(self.retriever.search, query_vectors[0], top_k)
        chunks = [chunk for chunk, _score in matches]
        draft = await self.provider.answer(query, chunks)
        contexts = [
            RetrievedContext(
                title=chunk.title,
                snippet=chunk.text,
                score=score,
                chunk_id=chunk.chunk_id,
            )
            for chunk, score in matches
        ]
        return QueryResponse(answer=draft.answer, contexts=contexts, reasoning=draft.reasoning)

    def health(self) -> HealthResponse:
        return HealthResponse(
            status=self.status,
            indexed_movies=self.indexed_movies,
            indexed_chunks=self.indexed_chunks,
            chat_model=self.settings.openai_chat_model,
            embedding_model=self.settings.openai_embedding_model,
            message=self.message,
        )

