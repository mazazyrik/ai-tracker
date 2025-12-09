from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from tortoise.expressions import Q

from app.db.models.task import Task, TaskStatus
from app.db.models.user import User


@dataclass
class TaskCreateData:
    user: User
    title: str
    planned_seconds: int
    task_date: date
    category: Optional[str] = None


async def create_task(data: TaskCreateData) -> Task:
    """Create new task."""
    task = await Task.create(
        user=data.user,
        title=data.title,
        planned_seconds=data.planned_seconds,
        date=data.task_date,
        category=data.category,
    )
    return task


async def list_tasks_for_date(user: User, task_date: date) -> List[Task]:
    """List tasks for date."""
    return await Task.filter(user=user, date=task_date).order_by('id')


async def list_active_or_planned_for_today(user: User, today: date) -> List[Task]:
    """List tasks that are not completed for today."""
    return await Task.filter(
        user=user,
        date=today,
    ).filter(
        Q(status=TaskStatus.PLANNED)
        | Q(status=TaskStatus.ACTIVE)
        | Q(status=TaskStatus.PAUSED),
    ).order_by('id')


async def get_task_for_user(task_id: int, user: User) -> Optional[Task]:
    """Get task by id for user."""
    return await Task.get_or_none(id=task_id, user=user)


async def update_status(task: Task, status: str) -> Task:
    """Update task status."""
    task.status = status
    await task.save()
    return task


async def add_spent_seconds(task: Task, seconds: int) -> Task:
    """Add spent seconds to task."""
    task.spent_seconds += seconds
    await task.save()
    return task


async def set_score(task: Task, score: Optional[int]) -> Task:
    """Set task score."""
    task.score = score
    await task.save()
    return task
