import asyncio
from typing import List
import logging
from dataclasses import dataclass
import uuid
from aiokafka.errors import KafkaConnectionError
from .base_consumer import MessageConsumer

logger = logging.getLogger(__name__)

from src.config import settings
from src.validator import conf_validator

event_loop = asyncio.get_event_loop()


@dataclass
class BrokerConfig:
    topic: str
    deployment_name: str
    deployment_id: uuid.UUID
    group_id: str
    bootstrap_servers: str


async def start_consumer(br_conf: BrokerConfig) -> None:
    consumer = MessageConsumer(
        topic=br_conf.topic,
        deployment_name=br_conf.deployment_name,
        deployment_id=br_conf.deployment_id,
        group_id=br_conf.group_id,
        bootstrap_servers=br_conf.bootstrap_servers,
        prefect_api_url=settings.prefect.prefect_api_url,
        loop=event_loop,
    )
    attempts = 0
    for i in range(settings.run_retry_limit):
        await consumer.consume_message(
            settings.prefect.basic_auth_username,
            settings.prefect.basic_auth_password,
        )

        if consumer.broker_started:
            logger.info("Starting consumer for topic: %s", br_conf.topic)
            break

        if not consumer.broker_started:
            logger.warning(
                "Consumer not started after %s attempts. Retrying",
                (attempts + 1),
            )
            await consumer.consumer.stop()
            attempts += 1
            await asyncio.sleep(2 + attempts)
        if attempts >= 5:
            logger.error("Consumer not started after 5 attempts")
            raise SystemExit(1)


background_tasks: List[asyncio.Task] = []


async def start_consumers() -> None:
    if not conf_validator.configs:
        raise RuntimeError("No configs found")

    for conf in conf_validator.configs:
        broker_config = BrokerConfig(
            topic=conf.topic,
            deployment_name=conf.deployment_name,
            deployment_id=conf.deployment_id,
            group_id=settings.broker.group_id,
            bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        )
        logger.info("Starting consumer for topic: %s", conf.topic)
        task = asyncio.create_task(start_consumer(broker_config))
        background_tasks.append(task)


async def stop_consumers() -> None:

    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)

    logger.info("All kafka consumers stopped")
