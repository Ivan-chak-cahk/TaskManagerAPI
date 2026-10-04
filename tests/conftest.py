import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.core.config import settings

# подключение к тестовой базе
test_engine = create_engine(settings.test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# настройка фикстур для дальнейших тестов
@pytest.fixture
def db():
    Base.metadata.create_all(bind=test_engine)  # создаём таблицы перед тестом

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)  # а после удаляем


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db
    # Если endpoint попросит get_db, вместо него берём override_get_db.
    # Благодаря этому API начинает работать с тестовой PostgreSQL.
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
