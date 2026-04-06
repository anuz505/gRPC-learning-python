"""FastAPI Service - HTTP API Gateway (delegates auth to gRPC Auth service)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import todo_routes
from db import init_db
from core import settings, logger
from schema import HealthCheckResponse
from api import todo_router
from api.auth_routes import auth_router
from services.auth_grpc_client import AuthGrpcClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting FastAPI application")
    
    try:
        # Initialize database
        init_db()
        logger.info("Todo database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    try:
        # Connect to Auth service
        AuthGrpcClient.get_channel()
        logger.info(f"Connected to Auth service: {settings.auth_service_host}:{settings.auth_service_port}")
    except Exception as e:
        logger.error(f"Failed to connect to Auth service: {e}")
        raise

    logger.info("Application startup complete")

    yield

    # Cleanup
    logger.info("Shutting down application")
    AuthGrpcClient.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(todo_router)


# Health check endpoint (no auth required)
@app.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="API health check endpoint"
)
async def root() -> HealthCheckResponse:
    """API health check."""
    return HealthCheckResponse(
        status="healthy",
        message="FastAPI service is running. All auth operations delegated to gRPC Auth service."
    )


# Startup message
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting FastAPI server on {settings.host}:{settings.port}")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
