from app.core.config import Settings


# значения по умолчанию, независимо от содержимого .env
def test_settings_defaults():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg2://user:pass@localhost/db",
        test_database_url="postgresql+psycopg2://user:pass@localhost/db_test",
        jwt_secret_key="test-secret",
    )

    assert settings.app_name == "Task Manager API"
    assert settings.app_version == "0.1.0"
    assert settings.debug is True
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
