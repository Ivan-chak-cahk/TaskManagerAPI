from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router
from app.core.config import settings
from app.core.exceptions import AppError

# создаём приложение
app = FastAPI(
    title=settings.app_name,
    description="REST API for task management",
    version=settings.app_version,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)

# Единое место, где ошибки бизнес-логики превращаются в HTTP-ответ
@app.exception_handler(AppError)  # слушаем всё приложение
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

# Когда придёт GET-запрос на /, вызывается функция root.
@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}
