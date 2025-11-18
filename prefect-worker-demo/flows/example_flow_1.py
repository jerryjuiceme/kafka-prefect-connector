from typing import TYPE_CHECKING, Union
import logging
from prefect import flow, get_run_logger, task


if TYPE_CHECKING:
    LoggingAdapter = logging.LoggerAdapter[logging.Logger]


@task(name="pipeline_start")
def start(logger: Union[logging.Logger, "LoggingAdapter"]):
    logger.info("Pipeline started")


@task(name="consume_message")
def consume_message(logger: Union[logging.Logger, "LoggingAdapter"], message: str):
    logger.info("Received message: %s " % message)
    return f"Final message: {message}"


@task(name="pipeline_end")
def end(logger: Union[logging.Logger, "LoggingAdapter"], message: str):
    logger.info("Pipeline ended. Message successfully consumed: %s " % message)


@flow(name="kafka_event_flow_1")
def kafka_event_pipeline_1(event_data: str):
    logger = get_run_logger()
    start(logger)
    message = consume_message(logger, event_data)
    end(logger, message)
