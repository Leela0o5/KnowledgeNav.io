# KnowledgeNav.io


KnowledgeNav.io lets you upload documents (PDF, DOCX, TXT, HTML), ask questions in a chat interface, and receive answers that are strictly grounded in your documents — every factual claim is backed by a `[SOURCE]` citation that links to the exact chunk it came from. Hallucinations are detected and blocked before they reach the user.

## Features

- **Hybrid retrieval** — BM25 keyword search + Cohere multilingual vector search, fused with Reciprocal Rank Fusion (RRF)
- **Cross-encoder reranking** — Cohere rerank-v3.5 scores the top candidates before generation
- **Strict citation enforcement** — LLM must cite every factual sentence; the pipeline validates coverage and rejects hallucinated chunk IDs, retrying if needed
- **Agentic workflow** — LangGraph graph with analyse → retrieve → rerank → generate → validate → persist nodes
- **Streaming responses** — Server-Sent Events deliver tokens as they arrive
- **Multi-corpus** — Create isolated corpora per project; documents are scoped to their corpus
- **OAuth authentication** — Google and GitHub login, JWT access + refresh token rotation
- **RAGAS evaluation** — Built-in evaluation pipeline measuring faithfulness, answer relevancy, context precision, and context recall

## Tech Stack

| Layer              | Technology                                       |
| ------------------ | ------------------------------------------------ |
| Frontend           | React 18, TypeScript, Vite, Tailwind CSS 4       |
| Backend            | FastAPI, Python 3.11, LangGraph, LangChain Core  |
| LLM                | Groq (llama-3.3-70b-versatile)                   |
| Embeddings         | Cohere embed-v3-multilingual                     |
| Reranking          | Cohere rerank-v3.5                               |
| Vector DB          | ChromaDB                                         |
| Keyword search     | rank-bm25                                        |
| Relational DB      | PostgreSQL 16 (asyncpg + SQLAlchemy 2)           |
| Cache / rate-limit | Redis 7                                          |
| Migrations         | Alembic                                          |
| Auth               | python-jose (JWT), Google OAuth2, GitHub OAuth   |
| Evaluation         | RAGAS                                            |
| Observability      | OpenTelemetry, LangSmith                         |
| CI/CD              | GitHub Actions, Railway (API), Vercel (frontend) |

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose

### Local setup

```bash
git clone https://github.com//Leela0o5/KnowledgeNav.io
cd KnowledgeNav.io

# Copy and fill in environment variables
cp .env.example .env


# Start infrastructure (PostgreSQL, Redis, ChromaDB)
docker compose up -d postgres redis chroma

# Install backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080

# Install and start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`. The API runs on `http://localhost:8080`.

### Docker Compose (full stack)

```bash
docker compose up
```

This starts the API, frontend, PostgreSQL, Redis, ChromaDB, and OpenTelemetry collector.

### Environment Variables

Copy `.env.example` to `.env` and fill in the required values.
See `.env.example` for all available settings and their defaults.

## Usage

1. **Sign in** with Google or GitHub on the landing page
2. **Create a corpus** — click "New Corpus" in the sidebar
3. **Upload documents** — click the upload icon and add PDF, DOCX, TXT, or HTML files
4. **Ask questions** — type in the chat input; responses stream with inline `[SOURCE]` citations
5. **Review citations** — click any citation to see the exact source chunk
6. **Switch corpora** — select a different corpus from the sidebar to query different document sets
7. **Manage sessions** — previous conversations are saved per corpus and accessible from the sidebar

## Contributing

1. Fork the repository and create a feature branch
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Run linting: `ruff check backend`
4. Run type checking: `mypy backend`
5. Run tests: `pytest`
6. Open a pull request against `main`

CI will run lint, type-check, unit tests, integration tests, and a frontend type-check on every PR.
