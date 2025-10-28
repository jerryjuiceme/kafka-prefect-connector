from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from uuid import UUID


class TopicToFlowConfig(BaseModel):
    deployment_name: str = Field(validation_alias="deploymentName")
    topic: str
    deployment_id: UUID = Field(validation_alias="deploymentId")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
