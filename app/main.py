from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.books import router as books_router
from app.core.config import settings


app = FastAPI(title=settings.app_name, version=settings.app_version)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok", "version": settings.app_version})


@app.get("/")
def index():
    return JSONResponse(
        content={
            "message": "Book Metadata and Recommendation API is running",
            "health": "/health",
            "docs": "/docs",
        }
    )


app.include_router(books_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
