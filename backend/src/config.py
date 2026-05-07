from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    COHERE_API_KEY: str
    COHERE_EMBED_MODEL: str = "embed-v3-multilingual"
    COHERE_RERANK_MODEL: str = "rerank-v3.5"
    COHERE_RERANK_TOP_N: int = 5

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_PREFIX: str = "knowledge_nav"

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    OAUTH_REDIRECT_BASE_URL: str = "http://localhost:3000"

    BM25_TOP_K: int = 20
    VECTOR_TOP_K: int = 20
    RRF_K: int = 60
    RERANK_TOP_N: int = 5

    MIN_CITATION_COVERAGE: float = 0.8
    CITATION_RETRY_LIMIT: int = 2

    SESSION_CONTEXT_TURNS: int = 6

    RAGAS_FAITHFULNESS_THRESHOLD: float = 0.85
    RAGAS_ANSWER_RELEVANCY_THRESHOLD: float = 0.80
    RAGAS_CONTEXT_PRECISION_THRESHOLD: float = 0.75
    RAGAS_CONTEXT_RECALL_THRESHOLD: float = 0.75

    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "knowledge-nav-prod"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    RATE_LIMIT_PER_MINUTE: int = 60
    LOG_LEVEL: str = "INFO"
    FRONTEND_URL: str = "http://localhost:3000"

    def ragas_thresholds(self) -> dict[str, float]:
        return {
            "faithfulness": self.RAGAS_FAITHFULNESS_THRESHOLD,
            "answer_relevancy": self.RAGAS_ANSWER_RELEVANCY_THRESHOLD,
            "context_precision": self.RAGAS_CONTEXT_PRECISION_THRESHOLD,
            "context_recall": self.RAGAS_CONTEXT_RECALL_THRESHOLD,
        }


settings = Settings()  