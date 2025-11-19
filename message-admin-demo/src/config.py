# src/config.py
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class BrokerConfig(BaseModel):

    kafka_bootstrap_servers: str
    group_id: str


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="allow",
    )
    base_dir: Path = BASE_DIR
    broker: BrokerConfig


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
