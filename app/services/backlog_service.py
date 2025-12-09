from datetime import date, timedelta
from typing import Dict, List

from app.db.models.task import Task, TaskStatus
from app.db.models.user import User


async def list_backlog(user: User, today: date, days: int = 30) -> Dict[date, List[Task]]:
    end = today + timedelta(days=days)
    tasks = await Task.filter(
        user=user,
        date__gte=today,
        date__lt=end,
    ).exclude(status=TaskStatus.COMPLETED).order_by('date', 'id')
    by_day: Dict[date, List[Task]] = {}
    for t in tasks:
        by_day.setdefault(t.date, []).append(t)
    return by_day


async def list_backlog_for_day(user: User, day: date) -> List[Task]:
    return await Task.filter(
        user=user,
        date=day,
    ).exclude(status=TaskStatus.COMPLETED).order_by('id')


async def cleanup_old_tasks(before: date) -> None:
    await Task.filter(date__lt=before).delete()


