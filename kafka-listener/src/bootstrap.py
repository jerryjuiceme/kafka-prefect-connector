from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.loggers import set_logging
from src.utils import name_to_snake
from src.healthcheck import router as healthcheck_router
from src.config import settings
from src.validator import conf_validator
from src.broker import start_consumers, stop_consumers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    set_logging()
    conf_validator.validate()
    await start_consumers()
    # startup
    yield
    # shutdown
    await stop_consumers()
    conf_validator.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=name_to_snake(settings.project_name),
        docs_url="/docs",
        openapi_url="/docs.json",
        version=settings.version,
    )
    app.include_router(healthcheck_router)
    return app
