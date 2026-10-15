def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Read documentation",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    task = response.json()
    assert task["title"] == "Learn FastAPI"
    assert task["description"] == "Read documentation"
    assert task["status"] == "new"
    assert task["priority"] == "medium"
    assert task["user_id"] is not None


def test_create_task_without_token(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Задача без авторизации",
        },
    )

    assert response.status_code == 401



def test_create_task_with_empty_title(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": ""},
    )

    assert response.status_code == 422



def test_get_tasks(client, auth_headers, task_factory):
    task_factory("Task 1")
    task_factory("Task 2")

    response = client.get("/tasks", headers=auth_headers)

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 2
    assert {task["title"] for task in tasks} == {"Task 1", "Task 2"}


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
def test_get_task_by_id(client, auth_headers, task_factory):
    task = task_factory("My task")

    response = client.get(
        f"/tasks/{task['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]
    assert response.json()["title"] == "My task"

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
def test_update_task(client, auth_headers, task_factory):
    task = task_factory(
        "Learn FastAPI",
        description="Read documentation",
    )

    response = client.patch(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"},
        headers=auth_headers,
    )

    assert response.status_code == 200

    updated_task = response.json()
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


def test_delete_task(client, auth_headers, task_factory):
    # создаём задачу
    task = task_factory("Task to delete")
    # удаляем её
    response = client.delete(
        f"/tasks/{task['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    # проверяем что задачи точно нет
    get_response = client.get(
        f"/tasks/{task['id']}",
        headers=auth_headers,
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
def test_filter_tasks_by_priority(client, auth_headers, task_factory):
    task_factory("Low priority task", priority="low")
    task_factory("High priority task", priority="high")
    task_factory("Medium priority task", priority="medium")

    response = client.get(
        "/tasks",
        params={"priority_filter": "high"},
        headers=auth_headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High priority task"
    assert tasks[0]["priority"] == "high"

# Совместная фильтрация
def test_filter_tasks_by_status_and_priority(client, auth_headers, task_factory):
    task_factory(
        "Matching task",
        status="in_progress",
        priority="high",
    )
    task_factory(
        "Wrong status",
        status="new",
        priority="high",
    )
    task_factory(
        "Wrong priority",
        status="in_progress",
        priority="low",
    )

    response = client.get(
        "/tasks",
        params={
            "status_filter": "in_progress",
            "priority_filter": "high",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Matching task"
    assert tasks[0]["status"] == "in_progress"
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


def test_task_pagination_with_filters(client, auth_headers, task_factory):
    for i in range(5):
        task_factory(
            f"High priority task {i}",
            priority="high",
        )

    task_factory("Low priority task", priority="low")

    response = client.get(
        "/tasks",
        params={
            "priority_filter": "high",
            "limit": 4,
            "offset": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 4
    assert all(task["priority"] == "high" for task in tasks)


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
