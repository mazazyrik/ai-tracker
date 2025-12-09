from datetime import date
from typing import Optional

import httpx

from app.core.config import Settings
from app.core.constants import APP_NAME
from app.db.models.user import User
from app.services.ai_prompts import SYSTEM_PROMPT, build_daily_prompt, build_weekly_prompt
from app.services.motivation_service import get_random_motivation
from app.services.stats_service import get_daily_stats, get_weekly_stats
from app.services.user_service import get_user_by_id


async def _call_yandex_gpt(settings: Settings, prompt: str) -> Optional[str]:
    headers = {
        'Authorization': f'Api-Key {settings.yandex_gpt.api_key}',
        'Content-Type': 'application/json',
        'X-Client-Request-ID': APP_NAME,
    }
    body = {
        'modelUri': f'gpt://{settings.yandex_gpt.folder_id}/yandexgpt-lite',
        'completionOptions': {
            'stream': False,
            'temperature': 0.3,
            'maxTokens': 800,
        },
        'messages': [
            {
                'role': 'system',
                'text': SYSTEM_PROMPT,
            },
            {
                'role': 'user',
                'text': prompt,
            },
        ],
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(settings.yandex_gpt.endpoint, headers=headers, json=body)
    if response.status_code != 200:
        return None
    data = response.json()
    alternatives = data.get('result', {}).get('alternatives') or []
    if not alternatives:
        return None
    first = alternatives[0]
    message = first.get('message') or {}
    return message.get('text')


async def generate_daily_summary(user_id: int, summary_date: date, settings: Settings) -> Optional[str]:
    user: Optional[User] = await get_user_by_id(user_id)
    if not user:
        return None
    stats = await get_daily_stats(user, summary_date)
    lines = []
    lines.append(f'Дата: {stats.day.isoformat()}')
    lines.append(f'Всего задач: {len(stats.tasks)}')
    lines.append(f'План по времени: {stats.planned_seconds // 60} минут')
    lines.append(f'Факт по времени: {stats.spent_seconds // 60} минут')
    if stats.tasks:
        lines.append('Задачи:')
        for t in stats.tasks:
            score_part = f', оценка {t.score}' if t.score is not None else ''
            lines.append(
                f'- {t.title}: план {t.planned_seconds // 60} мин, факт {t.spent_seconds // 60} мин, статус {t.status}{score_part}',
            )
    prompt = build_daily_prompt(lines)
    return await _call_yandex_gpt(settings, prompt)


async def generate_weekly_report(user_id: int, week_start: date, settings: Settings) -> Optional[str]:
    user: Optional[User] = await get_user_by_id(user_id)
    if not user:
        return None
    weekly = await get_weekly_stats(user, week_start)
    lines: list[str] = []
    lines.append(f'Неделя: {weekly.start.isoformat()} - {weekly.end.isoformat()}')
    for day, stats in weekly.by_day.items():
        lines.append(
            f'{day.isoformat()}: задач {len(stats.tasks)}, план {stats.planned_seconds // 60} мин, факт {stats.spent_seconds // 60} мин',
        )
    prompt = build_weekly_prompt(lines)
    return await _call_yandex_gpt(settings, prompt)


async def generate_all_done_message(user_id: int, day: date, settings: Settings) -> Optional[str]:
    _ = day  # не используется, но оставляем сигнатуру
    _ = settings
    user: Optional[User] = await get_user_by_id(user_id)
    if not user:
        return None
    return get_random_motivation()
