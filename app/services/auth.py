from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

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
        raise ValueError("Username or email already exists")
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
        raise ValueError("Username or email already exists") from error

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
        raise ValueError("Invalid email or password")  # Если его нет или неактивен

    if not verify_password(password, user.password_hash):  # Если есть — проверяем пароль
        raise ValueError("Invalid email or password")
    # если пароль правильный
    return create_access_token(str(user.id))
