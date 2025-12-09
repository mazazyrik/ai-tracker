from app.core.config import Settings


def get_tortoise_config(settings: Settings) -> dict[str, object]:
    return {
        'connections': {
            'default': settings.db.url,
        },
        'apps': {
            'models': {
                'models': [
                    'app.db.models.user',
                    'app.db.models.task',
                    'app.db.models.active_timer',
                ],
                'default_connection': 'default',
            },
        },
    }
