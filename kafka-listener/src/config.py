from functools import lru_cache
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class BrokerConfig(BaseModel):
    kafka_bootstrap_servers: str
    group_id: str


class PrefectConfig(BaseModel):
    api_url: str
    # basic auth for varible Example: PREFECT_API_AUTH_STRING="admin:pass"
    basic_auth_username: str
    basic_auth_password: str
    use_deployment_id: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env.template", BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="allow",
    )
    base_dir: Path = BASE_DIR
    project_name: str
    version: str
    mode: Literal["DEV", "PROD", "TEST"] = "DEV"
    broker: BrokerConfig
    prefect: PrefectConfig
    run_retry_limit: int


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
