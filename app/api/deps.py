from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

# При вызове сессия запустилась, отработала, автоматически закрылась
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
