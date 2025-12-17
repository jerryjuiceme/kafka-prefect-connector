import asyncio
import logging

from src.config import settings
from src.validator import conf_validator

from .base_consumer import MessageConsumer, PrefectConsumerConfig


logger = logging.getLogger(__name__)

event_loop = asyncio.get_event_loop()


async def start_consumer(br_conf: PrefectConsumerConfig) -> None:
    consumer = MessageConsumer(
        broker_config=br_conf,
        loop=event_loop,
        group_id=settings.broker.group_id,
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        prefect_api_url=settings.prefect.api_url,
    )
    attempts = 0
    for i in range(settings.run_retry_limit):
        await consumer.consume_message()

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
            await asyncio.sleep(3 + attempts)
        if attempts >= settings.run_retry_limit:
            logger.error(
                "Consumer not started, retry limit exceeded. Check Kafka Connection. Exiting"
            )
            raise SystemExit(1)


background_tasks: list[asyncio.Task] = []


async def start_consumers() -> None:
    if not conf_validator.configs:
        raise RuntimeError("No configs found")

    for conf in conf_validator.configs:

        ### if deployment id is not provided, use deployment name
        ### or if USE_DEPLOYMENT_ID=False in settings, use deployment name
        if not settings.prefect.use_deployment_id:
            deployment_id = conf.deployment_name
            logger.info(
                "USE_DEPLOYMENT_ID=False in settings. Using deployment name: %s",
                deployment_id,
            )
        elif conf.deployment_id is None:
            deployment_id = conf.deployment_name
            logger.info(
                "Deployment id not provided for topic: %s. Using deployment name: %s",
                conf.topic,
                deployment_id,
            )
        else:
            deployment_id = conf.deployment_id

        broker_config = PrefectConsumerConfig(
            topic=conf.topic,
            deployment_id=deployment_id,
            flow_name=conf.flow_name,
        )
        logger.info("Starting consumer for topic: %s", conf.topic)
        task = asyncio.create_task(start_consumer(broker_config))
        background_tasks.append(task)


async def stop_consumers() -> None:

    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)

    logger.info("All kafka consumers stopped")
