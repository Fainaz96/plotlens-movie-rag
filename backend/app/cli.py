from __future__ import annotations

import argparse
import asyncio
import json

from app.config import get_settings
from app.service import RAGService


async def run_query(question: str, top_k: int) -> None:
    service = RAGService(get_settings())
    await service.build()
    response = await service.query(question, top_k)
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask PlotLens a movie-plot question.")
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=5, choices=range(1, 9))
    args = parser.parse_args()
    asyncio.run(run_query(args.question, args.top_k))


if __name__ == "__main__":
    main()

