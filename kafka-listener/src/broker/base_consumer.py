import asyncio
from asyncio import AbstractEventLoop
import logging
from typing import Self
import uuid
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

import httpx


logger = logging.getLogger(__name__)


class MessageConsumer:
    def __init__(
        self,
        topic: str,
        deployment_name: str,
        deployment_id: uuid.UUID,
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
            max_poll_records=10,  # limit the number of records
            max_poll_interval_ms=5000,  # increase polling interval
        )
        self.topic: str = topic
        self.deployment_name: str = deployment_name
        self.deployment_id: uuid.UUID = deployment_id
        self.prefect_api_url: str = prefect_api_url
        self.broker_started = False

    async def consume_message(
        self: Self,
        auth_username: str | None,
        auth_password: str | None,
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
                    name=self.deployment_name,
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
        name: str,
        deployment_id: uuid.UUID,
        username: str | None,
        password: str | None,
    ) -> None:
        if username is None or password is None:
            auth = None
        else:
            auth = httpx.BasicAuth(username=username, password=password)

        async with httpx.AsyncClient(timeout=10, auth=auth) as client:
            url = f"{self.prefect_api_url}/deployments/{deployment_id}/create_flow_run"
            payload = {"parameters": {"event_data": message_value}}
            logger.info(
                "Message received %s. Triggering api for deployment '%s' (id=%s)",
                message_value,
                name,
                deployment_id,
            )

            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                logger.info(
                    "Flow run triggered for deployment '%s' (id=%s): %s",
                    name,
                    deployment_id,
                    result.get("id"),
                )
            except httpx.RequestError as exc:
                logger.error(" Prefect API request failed: %s", exc)
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Prefect API returned error %s: %s",
                    exc.response.status_code,
                    exc.response.text,
                )

    ################################################
    ############ Prefect SDK Method ################
    ################################################

    # async def trigger_flow(
    #     self,
    #     message_value: dict,
    #     name: str,
    #     deployment_id: uuid.UUID,
    # ):
    #   from prefect.client.orchestration import get_client
    #
    #     async with get_client() as client:
    #         await client.create_flow_run_from_deployment(
    #             name=name,
    #             deployment_id=deployment_id,
    #             parameters={"event_data": message_value},
    #         )
