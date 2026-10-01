from pydantic_settings import BaseSettings, SettingsConfigDict

# настройки приложения
class Settings(BaseSettings):
    app_name: str = "Task Manager API"
    app_version: str = "0.1.0"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()