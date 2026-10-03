from sqlalchemy import select

from app.core.security import verify_password
from app.db.database import SessionLocal
from app.db.models import User
from app.schemas.user import UserCreate
from app.services.auth import register_user


def test_register_user():
    db = SessionLocal()

    try:
        user_data = UserCreate(
            username="test_user",
            email="test@example.com",
            password="super-secret-password",
        )

        user = register_user(db, user_data)

        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.is_active is True

        assert user.password_hash != user_data.password
        assert verify_password(
            user_data.password,
            user.password_hash,
        )
    finally:
        db.query(User).filter(User.username == "test_user").delete()
        db.commit()
        db.close()
