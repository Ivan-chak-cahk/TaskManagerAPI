from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import Task, User
from app.schemas.task import TaskCreate

# Сохранение задачи в БД
def create_task(
    db: Session,  # сессия SQLAlchemy, через которую работаем с базой данных
    task_data: TaskCreate,  # проверенные Pydantic данные новой задачи
    user: User,  # авторизованный пользователь, от имени которого создаётся задача
) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        user_id=user.id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

# получение списка задач пользователя
def get_user_tasks(db: Session, user: User) -> list[Task]:
    statement = (
        select(Task)
        .where(Task.user_id == user.id)
        .order_by(Task.created_at.desc())
    )

    return list(db.scalars(statement).all())
