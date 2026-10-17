import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.core.config import settings

# после каждого теста все таблицы удаляются, поэтому тесты
# нельзя запускать на рабочей базе
if not settings.test_database_url or "test" not in (
    make_url(settings.test_database_url).database or ""
):
    raise RuntimeError(
        "TEST_DATABASE_URL должен указывать на тестовую базу "
        "(в её названии должно быть слово 'test')"
    )

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
    # возвращает тестовую сессию db, которую мы получили из параметров фикстуры
    def override_get_db():
        yield db
    # подмена зависимости, что бы в место обычной ДБ работала тестовая
    app.dependency_overrides[get_db] = override_get_db
    # запуск тестовой версии приложения
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_data():
    return {
        "username": "ivan",
        "email": "ivan@example.com",
        "password": "strongpassword123",
    }


@pytest.fixture
def auth_headers(client, user_data):
    register_response = client.post(
        "/auth/register",
        json=user_data,
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

# фабрика для создания тестовых задач
@pytest.fixture
def task_factory(client, auth_headers):
    def create_task(title="Test task", **overrides):
        # Код объединяет дефолтный title и все переданные через **overrides поля в один словарь
        payload = {"title": title, **overrides}

        response = client.post(
            "/tasks",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        return response.json()
    # Фикстура возвращает саму функцию create_task (без круглых скобок, то есть ссылку на неё), делая её доступной в тестах.
    return create_task


@pytest.fixture
def user_factory(client):
    def create_user(
        username,
        email,
        password="strongpassword123",
    ):
        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }

        register_response = client.post(
            "/auth/register",
            json=user_data,
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        return {
            "id": register_response.json()["id"],
            "username": username,
            "email": email,
            "password": password,
            "headers": {
                "Authorization": f"Bearer {token}",
            },
        }

    return create_user
