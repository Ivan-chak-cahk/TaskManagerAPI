from pydantic import BaseModel, EmailStr, Field, field_validator


# Добавляем схемы авторизации
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(max_length=28)
    # так же приводим к нижнему регистру
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
