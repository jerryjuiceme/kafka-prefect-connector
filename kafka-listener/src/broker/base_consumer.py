import asyncio
from asyncio import AbstractEventLoop
from functools import cache
import logging
from typing import Self
import uuid
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


# TODO: add linters
class MessageConsumer:
    def __init__(
        self,
        topic: str,
        deployment_id: uuid.UUID | str,
        flow_name: str,
        group_id: str,
        bootstrap_servers: str,
        prefect_api_url: str,
        loop: AbstractEventLoop,  # NOQA
    ):
        self.consumer = AIOKafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            # loop=loop,  # use custom event loop instance if needed
            max_poll_records=10,  # number of records
            max_poll_interval_ms=5000,  # polling interval
        )
        self.topic: str = topic
        self.deployment_id: uuid.UUID | str = deployment_id
        self.flow_name: str = flow_name
        self.prefect_api_url: str = prefect_api_url
        self.broker_started = False

    async def consume_message(
        self: Self,
        auth_username: str,
        auth_password: str,
    ) -> None:

        try:
            await self.consumer.start()
            self.broker_started = True
            logger.info("Consumer started, topic: %s", self.topic)

            async for message in self.consumer:
                if message.value is not None:
                    decoded_message = message.value.decode("utf-8")
                await self.trigger_flow(
                    message_value=decoded_message,
                    deployment_id=self.deployment_id,
                    username=auth_username,
                    password=auth_password,
                )
                await asyncio.sleep(0)

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt. Stopping consumer!")
            await self.consumer.stop()
        except KafkaConnectionError as e:
            logger.error(" Kafka connection error: %s", e)
            # raise e
        except asyncio.CancelledError:
            logger.warning("Consumer task cancelled.")
            raise
        finally:
            if self.broker_started:
                await self.consumer.stop()
                logger.info("Consumer stopped, topic: %s", self.topic)
                self.broker_started = False

    async def trigger_flow(
        self,
        message_value: dict,
        deployment_id: uuid.UUID | str,
        username: str,
        password: str,
    ) -> None:

        auth = httpx.BasicAuth(username=username, password=password)

        async with httpx.AsyncClient(timeout=10, auth=auth) as client:
            try:
                deployment_id = await self._get_deployment_id(
                    dp_name=deployment_id,
                    client=client,
                )
                url = f"{self.prefect_api_url}/deployments/{deployment_id}/create_flow_run"
                payload = {"parameters": {"event_data": message_value}}
                logger.info(
                    "Message received %s. Triggering api for deployment '%s'",
                    message_value,
                    deployment_id,
                )

                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                logger.info(
                    "Flow run triggered for deployment '%s': %s",
                    deployment_id,
                    result.get("id"),
                )
            except httpx.RequestError as e:
                logger.error(" Prefect API request failed: %s", e)
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Prefect API returned error %s: %s",
                    e.response.status_code,
                    e.response.text,
                )

    async def _get_deployment_id(
        self,
        dp_name: str | uuid.UUID,
        client: httpx.AsyncClient,
    ) -> uuid.UUID:
        if isinstance(dp_name, uuid.UUID):
            return dp_name

        logger.info("Fetching deployment id for deployment name: %s", dp_name)
        url = f"{self.prefect_api_url}/deployments/name/{self.flow_name}/{dp_name}"
        try:
            lookup_resp = await client.get(url)
            lookup_resp.raise_for_status()

            deployment = lookup_resp.json()
            if isinstance(deployment, list):
                deployment = deployment[0]

            self.deployment_id = uuid.UUID(deployment["id"])
            return self.deployment_id
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise
