from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskResponse(BaseModel):
    # позволяет Pydantic формировать ответ непосредственно из SQLAlchemy-объекта Task, а не только из словаря.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    user_id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
