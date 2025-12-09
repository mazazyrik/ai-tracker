import json
import random
from pathlib import Path
from typing import List


_MESSAGES: List[str] = []


def _load_messages() -> List[str]:
    if _MESSAGES:
        return _MESSAGES
    path = Path(__file__).with_name('motivation_messages.json')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return ['Все задачи завершены. Ты молодец, что довёл день до конца.']
    if not isinstance(data, list):
        return ['Все задачи завершены. Ты молодец, что довёл день до конца.']
    _MESSAGES.extend(str(item) for item in data)
    return _MESSAGES


def get_random_motivation() -> str:
    messages = _load_messages()
    if not messages:
        return 'Все задачи завершены. Ты молодец, что довёл день до конца.'
    return random.choice(messages)


