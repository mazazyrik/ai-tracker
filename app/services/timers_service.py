from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from redis.asyncio import Redis

from app.core.constants import REDIS_ACTIVE_TIMER_PREFIX
from app.db.models.task import Task, TaskStatus


@dataclass
class ActiveTimerData:
    task_id: int
    started_at: datetime
    accumulated_seconds: int
    chat_id: Optional[int]
    message_id: Optional[int]
    last_update_at: Optional[datetime]


def _key(task_id: int) -> str:
    return f'{REDIS_ACTIVE_TIMER_PREFIX}{task_id}'


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def get_active_timer(redis: Redis, task_id: int) -> Optional[ActiveTimerData]:
    raw = await redis.hgetall(_key(task_id))
    if not raw:
        return None
    started_at_str = raw.get('started_at')
    accumulated_str = raw.get('accumulated_seconds')
    if not started_at_str or accumulated_str is None:
        return None
    started_at = datetime.fromisoformat(started_at_str)
    accumulated_seconds = int(accumulated_str)
    chat_id_str = raw.get('chat_id')
    message_id_str = raw.get('message_id')
    last_update_str = raw.get('last_update_at')
    chat_id = int(chat_id_str) if chat_id_str is not None else None
    message_id = int(message_id_str) if message_id_str is not None else None
    last_update_at = datetime.fromisoformat(last_update_str) if last_update_str else None
    return ActiveTimerData(
        task_id=task_id,
        started_at=started_at,
        accumulated_seconds=accumulated_seconds,
        chat_id=chat_id,
        message_id=message_id,
        last_update_at=last_update_at,
    )


async def start_timer(redis: Redis, task: Task, chat_id: Optional[int], message_id: Optional[int]) -> None:
    now = _now_utc()
    mapping = {
        'started_at': now.isoformat(),
        'accumulated_seconds': task.spent_seconds,
    }
    if chat_id is not None:
        mapping['chat_id'] = str(chat_id)
    if message_id is not None:
        mapping['message_id'] = str(message_id)
    mapping['last_update_at'] = now.isoformat()
    await redis.hset(_key(task.id), mapping=mapping)
    task.status = TaskStatus.ACTIVE
    await task.save()


async def pause_timer(redis: Redis, task: Task) -> int:
    data = await get_active_timer(redis, task.id)
    if not data:
        return task.spent_seconds
    now = _now_utc()
    delta = int((now - data.started_at).total_seconds())
    total = data.accumulated_seconds + max(delta, 0)
    await redis.delete(_key(task.id))
    task.status = TaskStatus.PAUSED
    task.spent_seconds = total
    await task.save()
    return total


async def stop_timer(redis: Redis, task: Task, completed: bool) -> int:
    total = await pause_timer(redis, task)
    if completed:
        task.status = TaskStatus.COMPLETED
        await task.save()
    return total


def format_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f'{hours:02d}:{minutes:02d}:{secs:02d}'
