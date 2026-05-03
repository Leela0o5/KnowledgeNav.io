import cohere

from knowledge_nav.retrieval.schema import ScoredChunk


class RateLimitError(Exception):
    def __init__(self, provider: str, retry_after: float | None = None) -> None:
        super().__init__(f"Rate limit exceeded for {provider}")
        self.provider = provider
        self.retry_after = retry_after


class UpstreamError(Exception):
    def __init__(self, provider: str, status: int) -> None:
        super().__init__(f"Upstream error from {provider}: {status}")
        self.provider = provider
        self.status = status


class CohereReranker:
    """Cross-encoder reranker using Cohere rerank API."""

    def __init__(self, client: cohere.AsyncClient, model: str, top_n: int) -> None:
        self._client = client
        self._model = model
        self._top_n = top_n

    async def rerank(self, query: str, candidates: list[ScoredChunk]) -> list[ScoredChunk]:
        if not candidates:
            return []
        try:
            response = await self._client.rerank(
                model=self._model,
                query=query,
                documents=[c.text for c in candidates],
                top_n=self._top_n,
                return_documents=True,
            )
        except cohere.TooManyRequestsError as exc:
            raise RateLimitError(provider="cohere", retry_after=None) from exc
        except cohere.ApiError as exc:
            raise UpstreamError(provider="cohere", status=exc.http_status or 500) from exc

        return [
            ScoredChunk(chunk=candidates[r.index].chunk, score=r.relevance_score)
            for r in response.results
        ]
