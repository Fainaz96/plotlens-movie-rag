from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.service import RAGService


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is not configured")
async def test_live_openai_query() -> None:
    service = RAGService(get_settings())
    await service.build()
    response = await service.query("Which movie features the HAL 9000 computer?", top_k=5)

    assert response.answer
    assert response.reasoning
    assert any(context.title == "2001: A Space Odyssey" for context in response.contexts)

