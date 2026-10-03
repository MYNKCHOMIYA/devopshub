from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    project_id: UUID
    task_id: UUID | None = None
    actor_id: UUID
    action: str = Field(min_length=1, max_length=50)
    metadata: dict = Field(default_factory=dict)


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    task_id: UUID | None
    actor_id: UUID
    action: str
    metadata: dict = Field(
	validation_alias ="activity_metadata",
    )
    created_at: datetime
