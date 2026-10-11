from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# endpoint "Мне нужен текущий авторизованный пользователь"
@router.get("/me", response_model=UserResponse)
def get_me(# В get_current_use проверяется авторизации, если всё ок нам вернётся пользователь.
    current_user: User = Depends(get_current_user),
):
    return current_user
