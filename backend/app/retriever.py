from typing import Any, cast
from uuid import uuid4

import chromadb

from app.models import PlotChunk


class ChromaRetriever:
    def __init__(self) -> None:
        client = chromadb.EphemeralClient()
        self.collection = client.create_collection(
            name=f"movie_plots_{uuid4().hex}",
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[PlotChunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Every chunk must have one embedding.")
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "source_id": chunk.source_id,
                    "title": chunk.title,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
            embeddings=cast(Any, embeddings),
        )

    def search(
        self, query_embedding: list[float], top_k: int
    ) -> list[tuple[PlotChunk, float]]:
        result = self.collection.query(
            query_embeddings=cast(Any, [query_embedding]),
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        ids = result["ids"][0]
        documents = (result["documents"] or [[]])[0]
        metadatas = (result["metadatas"] or [[]])[0]
        distances = (result["distances"] or [[]])[0]

        matches: list[tuple[PlotChunk, float]] = []
        for chunk_id, document, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=True
        ):
            typed_metadata = cast(dict[str, Any], metadata)
            chunk = PlotChunk(
                chunk_id=chunk_id,
                source_id=str(typed_metadata["source_id"]),
                title=str(typed_metadata["title"]),
                chunk_index=int(typed_metadata["chunk_index"]),
                text=document,
            )
            score = round(max(0.0, min(1.0, 1.0 - float(distance))), 4)
            matches.append((chunk, score))
        return matches
