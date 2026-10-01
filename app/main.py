from fastapi import FastAPI

# создаём приложение
app = FastAPI(
    title="Task Manager API",
    description="REST API for task management",
    version="0.1.0",
)

# Когда придёт GET-запрос на /, вызывается функцию root.
@app.get("/")
def root():
    return {"message": "Task Manager API is running"}
