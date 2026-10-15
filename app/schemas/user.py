from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


# входные данные при регистрации
class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-zА-Яа-яЁё0-9_]+$",  # лат, кирил, цифры и _
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=28)

    # "Ivan@Example.com" и "ivan@example.com" - один и тот же email
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


# то, что API может вернуть клиенту после регистрации
class UserResponse(BaseModel):
    # берем значения непосредственно из атрибутов SQLAlchemy-модели
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool
