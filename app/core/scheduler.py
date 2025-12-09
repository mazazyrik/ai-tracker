from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import asyncio


AsyncJob = Callable[[], Awaitable[None]]


@dataclass
class ScheduledJob:
    task: asyncio.Task


async def run_periodic(job: AsyncJob, interval_seconds: float) -> None:
    while True:
        await job()
        await asyncio.sleep(interval_seconds)


def schedule_periodic(job: AsyncJob, interval_seconds: float) -> ScheduledJob:
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_periodic(job, interval_seconds))
    return ScheduledJob(task=task)
