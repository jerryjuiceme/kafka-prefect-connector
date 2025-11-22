from dataclasses import dataclass
import json
import logging

from src.config import settings
from src.validator.config_schema import TopicToFlowConfig


logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    flow_config: list[TopicToFlowConfig] | None = None

    def validate(self) -> None:
        logger.info("Validating validation config JSON file")
        try:
            config_dict = self._load_json()
            logger.debug("Loaded validation config JSON file: %s" % config_dict)

            self.flow_config = [
                TopicToFlowConfig.model_validate(i) for i in config_dict
            ]
        except OSError as e:
            logger.error("Failed to load validation config JSON file: %s" % e)
            raise
        except ValueError as e:
            logger.error("Failed to validate config JSON file: %s" % e)
            raise
        else:
            logger.info("Validation config JSON completed successfully")
            logger.debug([i.model_dump() for i in self.flow_config])

    def stop(self) -> None:
        self.flow_config = None
        logger.info("Validation config JSON stopped successfully")

    @property
    def configs(self) -> list | None:
        if self.flow_config:
            return self.flow_config
        else:
            return None

    def _load_json(self) -> dict:
        files = [
            settings.base_dir.parent / "kafka-prefect-config.json",
            settings.base_dir / "prefect_topics_config/kafka-prefect-config.json",
        ]
        for file in files:
            if file.exists():
                with open(file) as f:
                    return json.load(f)

        logger.error("Failed to load validation config JSON file")
        raise FileNotFoundError("Failed to load validation config JSON file")


conf_validator = ValidationConfig()
