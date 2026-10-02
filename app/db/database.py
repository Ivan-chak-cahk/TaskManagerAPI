from sqlalchemy import create_engine, text

from app.core.config import settings


engine = create_engine(settings.database_url)


def check_database_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
