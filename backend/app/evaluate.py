from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from app.config import get_settings
from app.service import RAGService


async def evaluate(path: Path) -> float:
    service = RAGService(get_settings())
    await service.build()
    cases = json.loads(path.read_text(encoding="utf-8"))
    hits = 0
    for case in cases:
        assert service.provider is not None
        assert service.retriever is not None
        vector = (await service.provider.embed([case["query"]]))[0]
        matches = service.retriever.search(vector, top_k=5)
        titles = [chunk.title for chunk, _score in matches]
        hit = case["expected_title"] in titles
        hits += int(hit)
        print(f"{'PASS' if hit else 'MISS'} | {case['query']} | {titles}")
    score = hits / len(cases)
    print(f"\nRecall@5: {hits}/{len(cases)} = {score:.0%}")
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure retrieval Recall@5.")
    parser.add_argument("--cases", type=Path, default=Path("evals/retrieval_cases.json"))
    args = parser.parse_args()
    asyncio.run(evaluate(args.cases))


if __name__ == "__main__":
    main()

