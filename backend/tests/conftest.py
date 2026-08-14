from __future__ import annotations

import hashlib

from app.models import AnswerDraft, PlotChunk


class FakeProvider:
    vocabulary = ("hal", "computer", "shark", "time", "toy", "alien", "ship", "mafia")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            lowered = text.casefold()
            vector = [float(lowered.count(term)) for term in self.vocabulary]
            if not any(vector):
                digest = hashlib.sha256(lowered.encode()).digest()
                vector = [byte / 255 for byte in digest[: len(self.vocabulary)]]
            vectors.append(vector)
        return vectors

    async def answer(self, query: str, contexts: list[PlotChunk]) -> AnswerDraft:
        if not contexts:
            return AnswerDraft(
                answer="I cannot determine that from the indexed plots.",
                reasoning="No retrieved context supports an answer.",
            )
        return AnswerDraft(
            answer=f"The retrieved movie is {contexts[0].title}.",
            reasoning=f"The plot for {contexts[0].title} contains the matching detail.",
        )

