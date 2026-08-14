from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class ServiceStatus(StrEnum):
    INITIALIZING = "initializing"
    READY = "ready"
    FAILED = "failed"


class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=8)

    @field_validator("query", mode="before")
    @classmethod
    def strip_query(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class RetrievedContext(BaseModel):
    title: str
    snippet: str
    score: float = Field(ge=0, le=1)
    chunk_id: str


class QueryResponse(BaseModel):
    answer: str
    contexts: list[RetrievedContext]
    reasoning: str


class AnswerDraft(BaseModel):
    answer: str = Field(description="A concise answer grounded only in the supplied context.")
    reasoning: str = Field(
        description="A short evidence summary naming what in the context supports the answer."
    )


class HealthResponse(BaseModel):
    status: ServiceStatus
    indexed_movies: int
    indexed_chunks: int
    chat_model: str
    embedding_model: str
    message: str | None = None


class MovieRow(BaseModel):
    source_id: str
    title: str
    plot: str


class PlotChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    chunk_index: int
    text: str

