from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from core import settings, logger
from schema import HealthCheckResponse
from contextlib import asynccontextmanager
from api import todo_router as todo_routes
from api.auth_routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    try:
        init_db()
        logger.info("Database initialized successfullly")
    except Exception as e:
        logger.error(f"Failed to initialize database {e}")
        raise

    logger.info("Application startup complete")

    yield

    logger.info("Shutting down application")
    # TODO
    logger.info("Application ShutDown Complete")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version
    )
app.include_router(auth_router)
app.include_router(todo_routes)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
