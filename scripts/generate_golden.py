import argparse
import asyncio
import json
from pathlib import Path

import anthropic

from knowledge_nav.config import settings
from knowledge_nav.ingestion.indexer import load_bm25_retriever
from knowledge_nav.retrieval.schema import ScoredChunk


_GENERATION_PROMPT = """Given the following document excerpt, generate a question and ground truth answer pair that tests factual retrieval.

Excerpt:
{excerpt}

Respond in JSON format:
{{
  "question": "...",
  "ground_truth": "..."
}}"""


async def _generate_pair(client: anthropic.AsyncAnthropic, chunk: ScoredChunk) -> dict[str, str] | None:
    response = await client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": _GENERATION_PROMPT.format(excerpt=chunk.text[:800])}],
    )
    text = response.content[0].text if response.content else ""
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return None


async def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap golden dataset from corpus")
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--bm25-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()

    retriever = load_bm25_retriever(args.corpus_id, args.bm25_dir)
    sample_chunks = retriever._chunks[: args.count]  # noqa: SLF001

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    pairs: list[dict[str, object]] = []
    for chunk in sample_chunks:
        scored = ScoredChunk(chunk=chunk, score=1.0)
        pair = await _generate_pair(client, scored)
        if pair is not None:
            pairs.append({
                "question": pair["question"],
                "ground_truth": pair["ground_truth"],
                "reference_chunks": [chunk.id],
            })

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

    print(f"Generated {len(pairs)} QA pairs. Review all entries before committing.")


if __name__ == "__main__":
    asyncio.run(main())
