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