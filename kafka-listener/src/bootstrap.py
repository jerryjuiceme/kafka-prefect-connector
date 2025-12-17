from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import httpx

from fastapi import FastAPI

from src.broker import start_consumers, stop_consumers
from src.config import settings
from src.healthcheck import router as healthcheck_router
from src.loggers import set_logging
from src.utils import name_to_snake
from src.validator import conf_validator
from src.http_client import http_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    set_logging()
    conf_validator.validate()
    http_client.init()
    await start_consumers()
    yield
    # shutdown
    await stop_consumers()
    await http_client.close()
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
