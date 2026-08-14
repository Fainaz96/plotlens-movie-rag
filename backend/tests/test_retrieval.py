from __future__ import annotations

from conftest import FakeProvider

from app.data import chunk_movies
from app.models import MovieRow
from app.retriever import ChromaRetriever


async def test_hal_query_retrieves_2001_first() -> None:
    provider = FakeProvider()
    chunks = chunk_movies(
        [
            MovieRow(
                source_id="1",
                title="2001: A Space Odyssey",
                plot="The HAL 9000 computer controls the ship and turns against the crew.",
            ),
            MovieRow(
                source_id="2",
                title="Jaws",
                plot="A police chief hunts a dangerous shark near a seaside town.",
            ),
            MovieRow(
                source_id="3",
                title="Toy Story",
                plot="A group of toys come alive when people are away.",
            ),
        ]
    )
    embeddings = await provider.embed([chunk.text for chunk in chunks])
    retriever = ChromaRetriever()
    retriever.add(chunks, embeddings)

    query_embedding = (await provider.embed(["Which film has the HAL computer on a ship?"]))[0]
    matches = retriever.search(query_embedding, top_k=3)

    assert matches[0][0].title == "2001: A Space Odyssey"
    assert 0 <= matches[0][1] <= 1
