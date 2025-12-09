from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List

from app.db.models.task import Task
from app.db.models.user import User


@dataclass
class DailyStats:
    day: date
    planned_seconds: int
    spent_seconds: int
    completed_tasks: int
    tasks: List[Task]


@dataclass
class WeeklyStats:
    start: date
    end: date
    by_day: Dict[date, DailyStats]


async def get_daily_stats(user: User, day: date) -> DailyStats:
    """Collect stats for day."""
    tasks = await Task.filter(user=user, date=day).order_by('id')
    planned = sum(t.planned_seconds for t in tasks)
    spent = sum(t.spent_seconds for t in tasks)
    completed = sum(1 for t in tasks if t.status == 'completed')
    return DailyStats(
        day=day,
        planned_seconds=planned,
        spent_seconds=spent,
        completed_tasks=completed,
        tasks=tasks,
    )


async def get_weekly_stats(user: User, start: date) -> WeeklyStats:
    """Collect stats for week starting from date."""
    by_day: Dict[date, DailyStats] = {}
    for i in range(7):
        day = start + timedelta(days=i)
        by_day[day] = await get_daily_stats(user, day)
    return WeeklyStats(start=start, end=start + timedelta(days=6), by_day=by_day)
