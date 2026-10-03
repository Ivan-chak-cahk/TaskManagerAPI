from pwdlib import PasswordHash

# pwdlib создаёт объект, который умеет хешировать и проверять пароли.
password_hash = PasswordHash.recommended()

# передаем функции пароль и хэшируем его
def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
