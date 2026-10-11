from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.core.config import settings
from app.api.routes.users import router as users_router

# создаём приложение
app = FastAPI(
    title=settings.app_name,
    description="REST API for task management",
    version=settings.app_version,
)

app.include_router(auth_router)
app.include_router(users_router)

# Когда придёт GET-запрос на /, вызывается функцию root.
@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}
