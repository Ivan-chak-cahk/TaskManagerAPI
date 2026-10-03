from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
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
        raise ValueError("Username or email already exists")
    # Создаём SQLAlchemy-модель
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
