from __future__ import annotations

from typing import Protocol

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.models import AnswerDraft, PlotChunk


class ProviderError(RuntimeError):
    """A safe, provider-neutral failure suitable for mapping to HTTP 502."""


class AIProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def answer(self, query: str, contexts: list[PlotChunk]) -> AnswerDraft: ...


class OpenAIProvider:
    def __init__(
        self,
        *,
        api_key: str,
        chat_model: str,
        embedding_model: str,
        timeout_seconds: float,
        batch_size: int,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=2)
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.batch_size = batch_size

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        try:
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start : start + self.batch_size]
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch,
                    encoding_format="float",
                )
                vectors.extend(item.embedding for item in response.data)
        except (APITimeoutError, RateLimitError, APIConnectionError, APIError) as exc:
            raise ProviderError("The AI provider could not create embeddings.") from exc
        return vectors

    async def answer(self, query: str, contexts: list[PlotChunk]) -> AnswerDraft:
        context_text = "\n\n".join(
            f"[Context {index}] Movie: {item.title}\n{item.text}"
            for index, item in enumerate(contexts, start=1)
        )
        instructions = (
            "You answer questions about movie plots using only the supplied retrieved contexts. "
            "If the contexts do not contain enough evidence, say that the answer cannot be "
            "determined from the indexed plots. Keep the answer concise. The reasoning field is a "
            "brief evidence summary, not hidden chain-of-thought: name the supporting movie and "
            "fact, or state that no context supports the answer. Never invent a movie or fact."
        )
        try:
            response = await self.client.responses.parse(
                model=self.chat_model,
                instructions=instructions,
                input=f"Question: {query}\n\nRetrieved contexts:\n{context_text}",
                text_format=AnswerDraft,
            )
        except (APITimeoutError, RateLimitError, APIConnectionError, APIError) as exc:
            raise ProviderError("The AI provider could not generate an answer.") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise ProviderError("The AI provider returned no structured answer.")
        return parsed

