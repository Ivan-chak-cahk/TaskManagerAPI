from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# тесты на проверку хеширования паролей
def test_hash_password():
    password = "super-secret-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password


def test_verify_password():
    password = "super-secret-password"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)


def test_same_password_has_different_hash():
    password = "super-secret-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash

# тесты для токенов
def test_create_and_decode_access_token():
    user_id = "123"

    token = create_access_token(user_id)
    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert "exp" in payload


def test_access_token_contains_user_id():
    token = create_access_token("42")

    payload = decode_access_token(token)

    assert payload["sub"] == "42"
