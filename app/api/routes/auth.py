from fastapi import APIRouter, Depends, HTTPException, status
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
    response_model=UserResponse,  # возвращаем из service полноценный объект User
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, user_data)
    except ValueError as error:  # Username or email already exists
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,  # указывает FastAPI, какой формат ответа мы ожидаем.
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    try:  # ищем пользователя в базе и проверяем пароль.
        access_token = authenticate_user(
            db,
            user_data.email,
            user_data.password,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }