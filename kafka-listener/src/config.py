from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class BrokerConfig(BaseModel):
    kafka_bootstrap_servers: str
    prefect_api_url: str
    group_id: str


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
    prefect_api_url: str


settings = Settings()  # type: ignore
