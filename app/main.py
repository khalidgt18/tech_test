from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import Base, engine
from app.routers import tickets


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Nothing to clean up for in-memory SQLite


settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="A mini REST API for ticket management",
    lifespan=lifespan,
)

# Include routers
app.include_router(tickets.router)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
