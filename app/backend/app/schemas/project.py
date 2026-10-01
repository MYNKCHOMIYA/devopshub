from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectPriority, ProjectStatus


class ProjectCreate(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.TODO
    priority: ProjectPriority = ProjectPriority.MEDIUM
    start_date: date | None = None
    due_date: date | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    status: ProjectStatus
    priority: ProjectPriority
    start_date: date | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
