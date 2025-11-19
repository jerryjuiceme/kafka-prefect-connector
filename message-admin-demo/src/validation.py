# src/validation.py
from dataclasses import dataclass
import json
import logging
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.config import settings

logger = logging.getLogger(__name__)


class TopicToFlowConfig(BaseModel):
    """Pydantic model for a single object from the JSON configuration."""

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
    """Class for validating and storing topic configuration."""

    flow_config: list[TopicToFlowConfig] | None = None

    def validate(self):
        """Loads and validates the JSON configuration file."""
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
        """Loads JSON from file."""
        with open(settings.base_dir / "prefect_data/event_config.json") as f:
            return json.load(f)

    @property
    def topics(self) -> list[str]:
        """Returns the list of topic names."""
        if self.flow_config:
            return [config.topic for config in self.flow_config]
        return []


# Create a single validator instance
conf_validator = ValidationConfig()
