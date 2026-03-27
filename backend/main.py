from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.upload import router as upload_router

app = FastAPI(
    title="AI Data Engineer API",
    version="1.0.0",
    description="Upload CSV files, clean data, infer schema, and generate basic insights."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api", tags=["data"])

@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}