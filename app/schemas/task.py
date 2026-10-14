from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    field_validator
)

from app.db.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.MEDIUM

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty or whitespace")

        return value


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
    # чтобы заголовок оставался необязательным при пропуске, но не мог быть явно задан как null.
    @model_validator(mode="after")
    def validate_title(self):
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Title cannot be null")
        return self
