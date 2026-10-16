from datetime import date, datetime

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
    due_date: date | None = None

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
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    user_id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None  # null допустим: так описание очищают
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None  # null допустим: так срок снимают

    # то же правило, что и при создании: заголовок без пробелов по краям и не пустой
    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        # strip() убирает пробелы
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty or whitespace")

        return value

    # Поля можно пропускать, но нельзя явно передавать null:
    # в БД они NOT NULL. Для description null разрешён.
    @model_validator(mode="after")
    def validate_not_null_fields(self):
        for field in ("title", "status", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self
