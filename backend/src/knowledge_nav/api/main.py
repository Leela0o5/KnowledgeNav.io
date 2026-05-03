from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledge_nav.api.middleware import TraceMiddleware
from knowledge_nav.api.routers import auth, health, ingest, messages, query, sessions
from knowledge_nav.config import settings

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
app.include_router(sessions.router)
app.include_router(messages.router)
app.include_router(query.router)
app.include_router(ingest.router)
