from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TopicToFlowConfig(BaseModel):
    deployment_name: str = Field(validation_alias="deploymentName")
    flow_name: str = Field(validation_alias="flowName")
    topic: str
    deployment_id: UUID | None = Field(validation_alias="deploymentId", default=None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
