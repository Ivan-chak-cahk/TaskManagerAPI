from fastapi import FastAPI

from app.core.config import settings

# создаём приложение
app = FastAPI(
    title=settings.app_name,
    description="REST API for task management",
    version=settings.app_version,
)

# Когда придёт GET-запрос на /, вызывается функцию root.
@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}
