from app.core.security import hash_password, verify_password

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
