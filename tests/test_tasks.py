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


def test_users_can_only_see_their_own_tasks(client, user_factory):
    first_user = user_factory("first_user", "first@example.com")
    second_user = user_factory("second_user", "second@example.com")

    first_task_response = client.post(
        "/tasks",
        json={"title": "Задача первого пользователя"},
        headers=first_user["headers"],
    )
    second_task_response = client.post(
        "/tasks",
        json={"title": "Задача второго пользователя"},
        headers=second_user["headers"],
    )

    assert first_task_response.status_code == 201
    assert second_task_response.status_code == 201

    first_response = client.get("/tasks", headers=first_user["headers"])
    second_response = client.get("/tasks", headers=second_user["headers"])

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_tasks = first_response.json()
    second_tasks = second_response.json()

    assert len(first_tasks) == 1
    assert len(second_tasks) == 1

    assert first_tasks[0]["title"] == "Задача первого пользователя"
    assert second_tasks[0]["title"] == "Задача второго пользователя"

    assert first_tasks[0]["user_id"] == first_user["id"]
    assert second_tasks[0]["user_id"] == second_user["id"]

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
def test_user_cannot_get_another_users_task(client, user_factory):
    owner = user_factory("owner_user", "owner@example.com")
    other_user = user_factory("other_user", "other@example.com")

    create_response = client.post(
        "/tasks",
        json={"title": "Чужая задача"},
        headers=owner["headers"],
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=other_user["headers"],
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
def test_user_cannot_update_another_users_task(client, user_factory):
    owner = user_factory("ivan", "ivan@example.com")
    other_user = user_factory("petr", "petr@example.com")

    task_response = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=owner["headers"],
    )
    assert task_response.status_code == 201

    task_id = task_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Hacked task"},
        headers=other_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/tasks/{task_id}",
        headers=owner["headers"],
    )
    assert owner_response.status_code == 200
    assert owner_response.json()["title"] == "Private task"


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


def test_user_cannot_delete_another_users_task(client, user_factory):
    owner = user_factory("ivan", "ivan@example.com")
    other_user = user_factory("petr", "petr@example.com")

    task_response = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=owner["headers"],
    )
    assert task_response.status_code == 201

    task_id = task_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=other_user["headers"],
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/tasks/{task_id}",
        headers=owner["headers"],
    )
    assert owner_response.status_code == 200
    assert owner_response.json()["title"] == "Private task"

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


def test_task_pagination(client, auth_headers, task_factory):
    for title in ["Task 1", "Task 2", "Task 3"]:
        task_factory(title)

    response = client.get(
        "/tasks",
        params={"limit": 2, "offset": 0},
        headers=auth_headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 2
    assert [task["title"] for task in tasks] == ["Task 3", "Task 2"]

    response = client.get(
        "/tasks",
        params={"limit": 2, "offset": 2},
        headers=auth_headers,
    )

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 1"


def test_task_pagination_rejects_invalid_parameters(client, auth_headers):
    invalid_queries = [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ]

    for params in invalid_queries:
        response = client.get(
            "/tasks",
            params=params,
            headers=auth_headers,
        )

        assert response.status_code == 422, (
            f"Ожидался статус 422 для параметров: {params}"
        )


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


def test_create_task_with_whitespace_title(client, auth_headers):
    response = client.post(
        "/tasks",
        json={"title": "   "},
        headers=auth_headers,
    )

    assert response.status_code == 422
