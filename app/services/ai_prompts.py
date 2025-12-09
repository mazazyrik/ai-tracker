from typing import Sequence


SYSTEM_PROMPT = 'Ты помощник по личной продуктивности. Отвечай кратко и по делу.'

DAILY_PROMPT_TEMPLATE = (
    'Сделай краткое саммари дня (5-10 предложений) по задачам и времени. '
    'Отметь, что получилось хорошо, что можно улучшить, и дай мягкие рекомендации. '
    'Вот данные по дню:\n{body}'
)

WEEKLY_PROMPT_TEMPLATE = (
    'Сделай отчёт по продуктивности за неделю (7-12 предложений). '
    'Сравни дни между собой, выдели прогресс и провалы, оцени фокус и устойчивость. '
    'Дай рекомендации на следующую неделю. '
    'Вот данные по неделе:\n{body}'
)


def build_daily_prompt(lines: Sequence[str]) -> str:
    body = '\n'.join(lines)
    return DAILY_PROMPT_TEMPLATE.format(body=body)


def build_weekly_prompt(lines: Sequence[str]) -> str:
    body = '\n'.join(lines)
    return WEEKLY_PROMPT_TEMPLATE.format(body=body)


