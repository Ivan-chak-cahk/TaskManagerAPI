def test_create_task(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "task_user",
            "email": "task_user@example.com",
            "password": "test_password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "task_user@example.com",
            "password": "test_password",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Изучить FastAPI",
            "description": "Добавить CRUD для задач",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Изучить FastAPI"
    assert data["description"] == "Добавить CRUD для задач"
    assert data["status"] == "new"
    assert data["priority"] == "medium"
    assert data["user_id"] == register_response.json()["id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_without_token(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Задача без авторизации",
        },
    )

    assert response.status_code == 401


def test_create_task_with_empty_title(client):
    register_response = client.post(
        "/auth/register",
        json={  # нужно не забывать создавать нового пользователя т.к после тестов он сбрасывается благодаря фикстуре.
            "username": "validation_user",
            "email": "validation_user@example.com",
            "password": "test_password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "validation_user@example.com",
            "password": "test_password",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "",
        },
    )

    assert response.status_code == 422
