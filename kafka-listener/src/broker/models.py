from dataclasses import dataclass
import uuid


@dataclass
class PrefectConsumerConfig:
    topic: str
    deployment_id: uuid.UUID | str
    flow_name: str
