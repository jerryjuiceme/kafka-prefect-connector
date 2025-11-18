from pathlib import Path
from flows import kafka_event_pipeline_2, kafka_event_pipeline_1


if __name__ == "__main__":
    kafka_event_pipeline_2.from_source(
        source=str(Path(__file__).parent),  # code stored in local directory
        entrypoint="deploy.py:kafka_event_pipeline_2",
    ).deploy(  # type: ignore
        name="process-kafka-deployment-2",
        description="Example Flow triggered via Kafka messages",
        work_pool_name="basic-pipe",
        version="0.0.1",
        tags=["example", "kafka"],
        push=False,
    )

    kafka_event_pipeline_1.from_source(
        source=str(Path(__file__).parent),
        entrypoint="deploy.py:kafka_event_pipeline_1",
    ).deploy(  # type: ignore
        name="process-kafka-deployment-1",
        description="Example Flow triggered via Kafka messages",
        work_pool_name="basic-pipe",
        version="0.0.1",
        tags=["example", "kafka"],
        push=False,
    )
