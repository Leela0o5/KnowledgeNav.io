import cohere

from knowledge_nav.config import settings


class Embedder:
    """Wraps Cohere embed API for query and document embedding."""

    def __init__(self, client: cohere.AsyncClient, model: str) -> None:
        self._client = client
        self._model = model

    async def embed_query(self, text: str) -> list[float]:
        response = await self._client.embed(
            texts=[text],
            model=self._model,
            input_type="search_query",
        )
        return list(response.embeddings[0])

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = await self._client.embed(
            texts=texts,
            model=self._model,
            input_type="search_document",
        )
        return [list(e) for e in response.embeddings]


def build_embedder() -> Embedder:
    client = cohere.AsyncClient(api_key=settings.COHERE_API_KEY)
    return Embedder(client=client, model=settings.COHERE_EMBED_MODEL)
