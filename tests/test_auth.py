def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "api_user",
            "email": "api@example.com",
            "password": "super-secret-password",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "api_user"
    assert data["email"] == "api@example.com"
    assert data["is_active"] is True

    assert "id" in data
    assert "created_at" in data

    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_user(client):
    user_data = {
        "username": "duplicate_user",
        "email": "duplicate@example.com",
        "password": "super-secret-password",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_current_user(client):
    # Регистрируем пользователя
    register_response = client.post(
        "/auth/register",
        json={
            "username": "me_test_user",
            "email": "me_test@example.com",
            "password": "super-secret-password",
        },
    )
    assert register_response.status_code == 201

    # Выполняем вход
    login_response = client.post(
        "/auth/login",
        json={
            "email": "me_test@example.com",
            "password": "super-secret-password",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Запрашиваем данные авторизованного пользователя
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "me_test_user"
    assert data["email"] == "me_test@example.com"
    assert "password_hash" not in data
    assert "password" not in data

# защищённый endpoint не доступен без токена.
def test_get_current_user_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_login_with_wrong_password(client):
    # Сначала регистрируем пользователя
    client.post(
        "/auth/register",
        json={
            "username": "wrong_password_user",
            "email": "wrong_password@example.com",
            "password": "correct-password",
        },
    )

    # Затем пробуем войти с неправильным паролем
    response = client.post(
        "/auth/login",
        json={
            "email": "wrong_password@example.com",
            "password": "incorrect-password",
        },
    )

    assert response.status_code == 401
