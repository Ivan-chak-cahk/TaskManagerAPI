from sqlalchemy import text

from app.db.database import check_database_connection


# проверка подключения к основной базе (только SELECT 1, данные не трогаем)
def test_database_connection():
    check_database_connection()


# и проверка сессии на тестовой базе
def test_database_session(db):
    result = db.execute(text("SELECT 1"))

    assert result.scalar() == 1
