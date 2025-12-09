from tortoise import Tortoise

from app.core.config import Settings
from app.db.config import get_tortoise_config


async def init_db(settings: Settings, with_schema: bool = True) -> None:
    await Tortoise.init(config=get_tortoise_config(settings))
    if with_schema:
        await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()


