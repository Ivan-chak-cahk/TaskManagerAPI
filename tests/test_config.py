from app.core.config import settings

# тест базовых настроек
def test_settings():
    assert settings.app_name == "Task Manager API"
    assert settings.app_version == "0.1.0"
    assert settings.debug is True