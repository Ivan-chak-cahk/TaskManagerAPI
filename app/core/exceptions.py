class AppError(Exception):
    """Централизованный обработчик ошибок для веб-приложения.
    Базовое исключение приложения. Сервисы бросают его наследников,
    а в HTTP-ответ их превращает обработчик в main.py."""

    status_code = 400
    default_detail = "Application error"
    headers: dict[str, str] | None = None
    # либо сами передаем что-то или берется значение default
    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        # передает это сообщение базовому классу Exception, чтобы оно корректно отображалось в логах и трейсбэке
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    default_detail = "Not found"


class ConflictError(AppError):
    status_code = 409
    default_detail = "Conflict"


class AuthenticationError(AppError):
    status_code = 401
    default_detail = "Authentication failed"
    headers = {"WWW-Authenticate": "Bearer"}
