"""FastAPI Main Application Entrypoint for Privacy-Preserving Federated Learning Platform."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import (
    orgs_router,
    training_router,
    metrics_ws_router,
    users_router,
    inference_router,
    node_telemetry_router,
    chat_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager: handles startup and shutdown events."""
    logger.info("Initializing database tables and Indian healthcare records...")
    init_db(force_reseed=True)
    logger.info(f"{settings.PROJECT_NAME} (v{settings.PROJECT_VERSION}) started successfully.")
    yield
    logger.info("Shutting down Federated Learning backend...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=(
            "Orchestration and integration layer for Privacy-Preserving Federated Learning platform (SIH). "
            "Connects React dashboards, Flower FL server, and privacy modules (Secure Aggregation + Differential Privacy)."
        ),
        lifespan=lifespan,
    )

    # Configure CORS middleware for local frontend development (React / Vite / Next.js / Browser)
    cors_origins = (
        settings.CORS_ORIGINS
        if isinstance(settings.CORS_ORIGINS, list)
        else [settings.CORS_ORIGINS]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if "*" not in cors_origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount REST & WebSocket Routers
    app.include_router(orgs_router)
    app.include_router(training_router)
    app.include_router(metrics_ws_router)
    app.include_router(users_router)
    app.include_router(inference_router)
    app.include_router(node_telemetry_router)
    app.include_router(chat_router)

    @app.post("/db/seed", tags=["Database"])
    def trigger_seed() -> dict:
        """Trigger a complete database wipe and re-seed with Indian healthcare data."""
        try:
            init_db(force_reseed=True)
            return {"status": "success", "message": "Database reseeded successfully with Indian entities."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @app.get("/", tags=["Health"])
    def root_status() -> dict:
        """Root status endpoint returning service metadata."""
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "status": "online",
            "docs_url": "/docs",
            "websocket_url": "/ws/metrics",
        }

    @app.get("/health", tags=["Health"])
    def health_check() -> JSONResponse:
        """Health check endpoint for container orchestrators and uptime monitors."""
        return JSONResponse(status_code=200, content={"status": "healthy"})

    return app


app = create_app()
