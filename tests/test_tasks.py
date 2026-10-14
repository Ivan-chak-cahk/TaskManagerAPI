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


def test_get_tasks(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "list_user",
            "email": "list_user@example.com",
            "password": "test_password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "list_user@example.com",
            "password": "test_password",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/tasks",
        headers=headers,
        json={"title": "Первая задача"},
    )
    client.post(
        "/tasks",
        headers=headers,
        json={"title": "Вторая задача"},
    )

    response = client.get("/tasks", headers=headers)
    # проверка получение списка задач
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {task["title"] for task in data} == {
        "Первая задача",
        "Вторая задача",
    }
    assert all(  # у каждой задачи правильный владелец
        task["user_id"] == register_response.json()["id"]
        for task in data
    )


def test_get_tasks_without_token(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_users_can_only_see_their_own_tasks(client):
    first_user = {
        "username": "first_user",
        "email": "first@example.com",
        "password": "test_password",
    }
    second_user = {
        "username": "second_user",
        "email": "second@example.com",
        "password": "test_password",
    }

    first_register = client.post("/auth/register", json=first_user)
    second_register = client.post("/auth/register", json=second_user)

    assert first_register.status_code == 201
    assert second_register.status_code == 201

    first_login = client.post(
        "/auth/login",
        json={
            "email": first_user["email"],
            "password": first_user["password"],
        },
    )
    second_login = client.post(
        "/auth/login",
        json={
            "email": second_user["email"],
            "password": second_user["password"],
        },
    )

    first_headers = {
        "Authorization": f"Bearer {first_login.json()['access_token']}"
    }
    second_headers = {
        "Authorization": f"Bearer {second_login.json()['access_token']}"
    }

    client.post(
        "/tasks",
        headers=first_headers,
        json={"title": "Задача первого пользователя"},
    )
    client.post(
        "/tasks",
        headers=second_headers,
        json={"title": "Задача второго пользователя"},
    )

    first_response = client.get("/tasks", headers=first_headers)
    second_response = client.get("/tasks", headers=second_headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_tasks = first_response.json()
    second_tasks = second_response.json()

    assert len(first_tasks) == 1
    assert len(second_tasks) == 1

    assert first_tasks[0]["title"] == "Задача первого пользователя"
    assert second_tasks[0]["title"] == "Задача второго пользователя"
    # пользователи видят свои задачи
    assert (
        first_tasks[0]["user_id"]
        == first_register.json()["id"]
    )
    assert (
        second_tasks[0]["user_id"]
        == second_register.json()["id"]
    )

# тест на получение задачи по id
def test_get_task_by_id(client):
    client.post(
        "/auth/register",
        json={
            "username": "detail_user",
            "email": "detail_user@example.com",
            "password": "test_password",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "detail_user@example.com",
            "password": "test_password",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Конкретная задача"},
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Конкретная задача"

# тест на недоступность чужой задачи
def test_user_cannot_get_another_users_task(client):
    first_user = {
        "username": "owner_user",
        "email": "owner@example.com",
        "password": "test_password",
    }
    second_user = {
        "username": "other_user",
        "email": "other@example.com",
        "password": "test_password",
    }

    client.post("/auth/register", json=first_user)
    client.post("/auth/register", json=second_user)

    owner_login = client.post(
        "/auth/login",
        json={
            "email": first_user["email"],
            "password": first_user["password"],
        },
    )
    other_login = client.post(
        "/auth/login",
        json={
            "email": second_user["email"],
            "password": second_user["password"],
        },
    )

    owner_headers = {
        "Authorization": f"Bearer {owner_login.json()['access_token']}"
    }
    other_headers = {
        "Authorization": f"Bearer {other_login.json()['access_token']}"
    }

    create_response = client.post(
        "/tasks",
        headers=owner_headers,
        json={"title": "Чужая задача"},
    )
    task_id = create_response.json()["id"]
    # пытаемся получить задачу другого пользователя
    response = client.get(
        f"/tasks/{task_id}",
        headers=other_headers,
    )

    assert response.status_code == 404

# Проверяем частичное обновление задачи
def test_update_task(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Read documentation",
        },
        headers=headers,
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=headers,
    )

    assert update_response.status_code == 200

    updated_task = update_response.json()
    assert updated_task["status"] == "in_progress"
    assert updated_task["title"] == "Learn FastAPI"
    assert updated_task["description"] == "Read documentation"
    assert updated_task["priority"] == "medium"

# Проверяем защиту чужих задач
def test_user_cannot_update_another_users_task(client):
    first_user = {
        "username": "ivan",
        "email": "ivan@example.com",
        "password": "strongpassword123",
    }
    second_user = {
        "username": "petr",
        "email": "petr@example.com",
        "password": "strongpassword123",
    }

    client.post("/auth/register", json=first_user)
    client.post("/auth/register", json=second_user)

    first_login = client.post(
        "/auth/login",
        json={
            "email": first_user["email"],
            "password": first_user["password"],
        },
    )
    first_token = first_login.json()["access_token"]
    first_headers = {"Authorization": f"Bearer {first_token}"}

    second_login = client.post(
        "/auth/login",
        json={
            "email": second_user["email"],
            "password": second_user["password"],
        },
    )
    second_token = second_login.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}
    # один юзер создал задачу
    task_response = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=first_headers,
    )
    task_id = task_response.json()["id"]
    # другой пытается изменить
    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Hacked task"},
        headers=second_headers,
    )

    assert update_response.status_code == 404
# Мб надо было авторизацию и регистрацию юзеров запихнуть в конфиг фикстуры.
# А то как-то громоздко всё

def test_delete_task(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks",
        json={"title": "Task to delete"},
        headers=headers,
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


def test_user_cannot_delete_another_users_task(client):
    first_user = {
        "username": "ivan",
        "email": "ivan@example.com",
        "password": "strongpassword123",
    }
    second_user = {
        "username": "petr",
        "email": "petr@example.com",
        "password": "strongpassword123",
    }

    client.post("/auth/register", json=first_user)
    client.post("/auth/register", json=second_user)

    first_login = client.post(
        "/auth/login",
        json={
            "email": first_user["email"],
            "password": first_user["password"],
        },
    )
    first_headers = {
        "Authorization": f"Bearer {first_login.json()['access_token']}"
    }

    second_login = client.post(
        "/auth/login",
        json={
            "email": second_user["email"],
            "password": second_user["password"],
        },
    )
    second_headers = {
        "Authorization": f"Bearer {second_login.json()['access_token']}"
    }

    task_response = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=first_headers,
    )
    task_id = task_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=second_headers,
    )

    assert delete_response.status_code == 404

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=first_headers,
    )
    assert get_response.status_code == 200

# Фильтрация по приоритету
def test_filter_tasks_by_priority(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/tasks",
        json={"title": "Low priority task", "priority": "low"},
        headers=headers,
    )
    client.post(
        "/tasks",
        json={"title": "High priority task", "priority": "high"},
        headers=headers,
    )

    response = client.get(
        "/tasks?priority_filter=high",
        headers=headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High priority task"
    assert tasks[0]["priority"] == "high"

# Совместная фильтрация
def test_filter_tasks_by_status_and_priority(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/tasks",
        json={
            "title": "New high priority",
            "status": "new",
            "priority": "high",
        },
        headers=headers,
    )
    client.post(
        "/tasks",
        json={
            "title": "In progress high priority",
            "status": "in_progress",
            "priority": "high",
        },
        headers=headers,
    )
    client.post(
        "/tasks",
        json={
            "title": "New low priority",
            "status": "new",
            "priority": "low",
        },
        headers=headers,
    )

    response = client.get(
        "/tasks?status_filter=new&priority_filter=high",
        headers=headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "New high priority"
    assert tasks[0]["status"] == "new"
    assert tasks[0]["priority"] == "high"


def test_task_pagination(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for title in ["Task 1", "Task 2", "Task 3"]:
        response = client.post(
            "/tasks",
            json={"title": title},
            headers=headers,
        )
        assert response.status_code == 201
    # должно вывести последние 2 созданные задачи
    response = client.get(
        "/tasks?limit=2&offset=0",
        headers=headers,
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert [task["title"] for task in tasks] == ["Task 3", "Task 2"]
    # offset=2 пропускаем первые две задачи
    response = client.get(
        "/tasks?limit=2&offset=2",
        headers=headers,
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 1"


def test_task_pagination_rejects_invalid_parameters(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # задаем неправильные параметры
    invalid_queries = [
        "/tasks?limit=0",
        "/tasks?limit=101",
        "/tasks?offset=-1",
    ]

    for query in invalid_queries:
        response = client.get(query, headers=headers)
        assert response.status_code == 422


def test_task_pagination_with_filters(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for title in ["High 1", "Low", "High 2"]:
        priority = "low" if title == "Low" else "high"
        response = client.post(
            "/tasks",
            json={
                "title": title,
                "status": "new",
                "priority": priority,
            },
            headers=headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/tasks?priority_filter=high&limit=1&offset=1",
        headers=headers,
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High 1"


def test_create_task_with_whitespace_title(client):
    client.post(
        "/auth/register",
        json={
            "username": "ivan",
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ivan@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    #
    response = client.post(
        "/tasks",
        json={"title": "   "},
        headers=headers,
    )

    assert response.status_code == 422
