import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.db.models import User

# используется для извлечения и автоматической валидации Bearer-токена
security = HTTPBearer()

# При вызове сессия запустилась, отработала, автоматически закрылась
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Аутентифицирует пользователя по Bearer-токену.
    Извлекает и декодирует JWT-токен, проверяет его валидность
    и ищет соответствующего пользователя в базе данных.
    Возвращает объект User или прерывает запрос с ошибкой 401 Unauthorized.
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # поиск пользователя
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user
