from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskRead(BaseModel):
    id: UUID
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: str | None
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class TaskStatusRead(BaseModel):
    id: UUID
    status: TaskStatus


class TaskListRead(BaseModel):
    items: list[TaskRead]
    total: int
    limit: int
    offset: int
