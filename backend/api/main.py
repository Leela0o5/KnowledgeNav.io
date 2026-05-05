from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware import TraceMiddleware
from api.routers import auth, corpora, health, ingest, messages, query, sessions
from src.config import settings

app = FastAPI(title="KnowledgeNav API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TraceMiddleware)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(corpora.router)
app.include_router(sessions.router)
app.include_router(messages.router)
app.include_router(query.router)
app.include_router(ingest.router)
