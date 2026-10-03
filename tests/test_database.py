from sqlalchemy import text

from app.db.database import SessionLocal, check_database_connection

# Проверка подключения
def test_database_connection():
    check_database_connection()

# и проверка сессии
def test_database_session():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        db.close()
