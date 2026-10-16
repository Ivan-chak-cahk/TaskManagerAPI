import pytest

from datetime import timedelta

from app.core.security import create_access_token
from app.db.models import User

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


def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_get_current_user_with_expired_token(client, user_factory):
    user = user_factory("expired_user", "expired@example.com")
    token = create_access_token(
        str(user["id"]),
        expires_delta=timedelta(minutes=-1),
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_inactive_user_cannot_use_api(client, db, user_factory):
    user = user_factory("inactive_user", "inactive@example.com")

    db_user = db.get(User, user["id"])
    db_user.is_active = False
    db.commit()

    response = client.get("/users/me", headers=user["headers"])

    assert response.status_code == 403


def test_inactive_user_cannot_login(client, db, user_factory):
    user = user_factory("inactive_login", "inactive_login@example.com")

    db_user = db.get(User, user["id"])
    db_user.is_active = False
    db.commit()

    response = client.post(
        "/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )

    assert response.status_code == 401

# тесты с параметром запустятся несколько раз
@pytest.mark.parametrize(
    "username",
    ["ab", "a" * 51, "bad name"],
)
def test_register_with_invalid_username(client, username):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": "valid@example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("password", ["short", "a" * 129])
def test_register_with_invalid_password(client, password):
    response = client.post(
        "/auth/register",
        json={
            "username": "valid_user",
            "email": "valid@example.com",
            "password": password,
        },
    )

    assert response.status_code == 422


def test_email_is_case_insensitive(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "case_user",
            "email": "Case.User@Example.com",
            "password": "strongpassword123",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "case.user@example.com"

    # вход с другим регистром
    login_response = client.post(
        "/auth/login",
        json={
            "email": "CASE.USER@example.com",
            "password": "strongpassword123",
        },
    )

    assert login_response.status_code == 200

    # повторная регистрация с другим регистром - дубликат
    duplicate_response = client.post(
        "/auth/register",
        json={
            "username": "other_user",
            "email": "case.user@EXAMPLE.com",
            "password": "strongpassword123",
        },
    )

    assert duplicate_response.status_code == 409


def test_login_error_response(client, user_factory):
    user_factory("login_user", "login@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_register_duplicate_error_response(client, user_factory):
    user_factory("dup_user", "dup@example.com")

    response = client.post(
        "/auth/register",
        json={
            "username": "dup_user",
            "email": "dup@example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username or email already exists"}
