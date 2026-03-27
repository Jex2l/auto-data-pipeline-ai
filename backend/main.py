from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.upload import router as upload_router
from backend.routes.query import router as query_router

app = FastAPI(
    title="Auto Data Pipeline AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(query_router, prefix="/api", tags=["query"])


@app.get("/")
def root() -> dict:
    return {
        "message": "Auto Data Pipeline AI backend is running."
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok"
    }