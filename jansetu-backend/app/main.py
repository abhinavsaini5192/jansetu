from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.database import check_database_connection
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import logger, setup_logging
from app.schemas.common import HealthResponse

# Setup structured logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown procedures."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")

    # Verify database connectivity status on startup
    if settings.DATABASE_URL.startswith("sqlite"):
        from app.models import Base
        from app.core.database import engine
        Base.metadata.create_all(bind=engine)
        logger.info("Local SQLite database verified and schema initialized.")

    db_check = check_database_connection()
    if db_check.get("status") == "connected":
        logger.info(f"Database connection verified: [{db_check.get('dialect')}] operational.")
    else:
        logger.warning(
            f"Database not currently accessible: {db_check.get('error_detail', 'offline')}. "
            "Server will continue serving health and standalone endpoints."
        )

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_application() -> FastAPI:
    """Factory function to build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "JanSetu API — AI-powered Societal Innovation and Collaboration Platform "
            "connecting citizens, government departments, universities, students, researchers, "
            "and CSR/industry partners."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Attach settings to state for global access if needed
    app.state.settings = settings

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register standardized error handlers
    register_exception_handlers(app)

    # Direct root health endpoint: GET /health
    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Service Health Check",
        tags=["Health"],
    )
    def root_health():
        return {"status": "healthy", "service": "jansetu-backend", "version": "1.0.0"}

    # Root index endpoint: GET /
    @app.get("/", summary="Root Welcome", tags=["Root"])
    def root():
        return {
            "message": "Welcome to JanSetu API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    # Mount versioned API routes under /api/v1
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)


    return app


app = create_application()
