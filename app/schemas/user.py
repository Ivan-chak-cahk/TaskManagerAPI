from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

# входные данные при регистрации
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# то, что API может вернуть клиенту после регистрации
class UserResponse(BaseModel):
    # берем значения непосредственно из атрибутов SQLAlchemy-модели
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool
