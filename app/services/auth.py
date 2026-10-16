from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:
    existing_user = db.scalar(  # Ищем существующего пользователя
        select(User).where(
            or_(
                User.username == user_data.username,
                User.email == user_data.email,
            )
        )
    )

    if existing_user is not None:
        raise ConflictError("Username or email already exists")
    # Создаём SQLAlchemy-модель
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()  # без rollback сессия останется в сломанном состоянии
        raise ConflictError("Username or email already exists") from error

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> str:
    user = db.scalar(  # ищем пользователя
        select(User).where(User.email == email)
    )

    if user is None or not user.is_active:
        raise AuthenticationError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    # если пароль правильный
    return create_access_token(str(user.id))
