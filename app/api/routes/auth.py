from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import authenticate_user, register_user

router = APIRouter(  # Все endpoints этого роутера будут относиться к /auth.
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):  # ошибки теперь ловятся через обработчик
    return register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    access_token = authenticate_user(
        db,
        user_data.email,
        user_data.password,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
