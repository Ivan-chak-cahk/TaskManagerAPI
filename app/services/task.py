from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models import Task, User
from app.db.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate

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
def get_user_tasks(
    db: Session,
    user: User,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
    limit: int = 20,
    offset: int = 0,  # пропускает указанное количество записей.
) -> list[Task]:
    statement = select(Task).where(Task.user_id == user.id)
    # выполнится если есть фильтр
    if status_filter is not None:
        statement = statement.where(Task.status == status_filter)
    if priority_filter is not None:
        statement = statement.where(Task.priority == priority_filter)
    # теперь возвращает макс 20 задач за раз
    statement = (
        statement
        .order_by(Task.created_at.desc(), Task.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(db.scalars(statement).all())

# получение одной конкретной задачи по ID
def get_task_by_id(
    db: Session,
    task_id: int,
    user: User,
) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,  # условие находит задачу по ID
            Task.user_id == user.id,  # ограничивает поиск задачами текущего пользователя
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


def update_task(
    db: Session,
    task_id: int,
    task_data: TaskUpdate,
    user: User,
) -> Task:
    task = get_task_by_id(db, task_id, user)
    # Получаем только переданные (измененные) поля
    update_data = task_data.model_dump(exclude_unset=True)
    # Обновляем атрибуты объекта
    for field, value in update_data.items():
        setattr(task, field, value)
    # setattr() позволяет менять атрибут объекта по имени, хранящемуся в строке.
    # Например, setattr(task, "title", "Новый заголовок") эквивалентен task.title = "Новый заголовок".
    db.commit()
    db.refresh(task)

    return task


def delete_task(
        db: Session,
        task_id: int,
        user: User
) -> None:
    task = get_task_by_id(db, task_id, user)

    db.delete(task)
    db.commit()
