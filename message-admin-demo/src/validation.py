# src/validation.py
from dataclasses import dataclass
import json
import logging
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.config import settings

logger = logging.getLogger(__name__)


class TopicToFlowConfig(BaseModel):
    """Pydantic модель для одного объекта из JSON-конфигурации."""

    deployment_name: str = Field(validation_alias="deploymentName")
    flow_name: str = Field(validation_alias="flowName")
    topic: str
    deployment_id: UUID = Field(validation_alias="deploymentId")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


@dataclass
class ValidationConfig:
    """Класс для валидации и хранения конфигурации топиков."""

    flow_config: list[TopicToFlowConfig] | None = None

    def validate(self):
        """Загружает и валидирует JSON-файл конфигурации."""
        logger.info("Validating validation config JSON file")
        try:
            config_dict = self._load_json()
            logger.debug("Loaded validation config JSON file: %s" % config_dict)

            self.flow_config = [
                TopicToFlowConfig.model_validate(i) for i in config_dict
            ]
        except FileNotFoundError as e:
            logger.error("Config JSON file not found: %s" % e)
            raise
        except Exception as e:
            logger.error("Failed to validate config JSON file: %s" % e)
            raise
        else:
            logger.info("Validation config JSON completed successfully")
            logger.debug([i.model_dump() for i in self.flow_config])

    def _load_json(self) -> dict:
        """Загружает JSON из файла."""
        with open(settings.base_dir / "prefect_data/event_config.json") as f:
            return json.load(f)

    @property
    def topics(self) -> list[str]:
        """Возвращает список имен топиков."""
        if self.flow_config:
            return [config.topic for config in self.flow_config]
        return []


# Создаем единственный экземпляр валидатора
conf_validator = ValidationConfig()
