import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as analyze_router


app = FastAPI(
    title="AI Secure Data Intelligence Platform",
    version="1.0.0",
    description=(
        "An AI-powered security platform that scans files, text, SQL, chat, and logs "
        "for sensitive data, secrets, anomalies, and operational risk."
    ),
)


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_URL") or "http://localhost:5173"
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


cors_origins = _cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    return {"status": "ok", "environment": os.getenv("APP_ENV", "development")}


frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
