from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class BotConfig:
    token: str


@dataclass
class DbConfig:
    url: str


@dataclass
class RedisConfig:
    url: str


@dataclass
class YandexGPTConfig:
    api_key: str
    folder_id: str
    endpoint: str


@dataclass
class CronConfig:
    daily_hour: int
    daily_minute: int
    morning_hour: int
    morning_minute: int
    weekly_weekday: int
    weekly_hour: int
    reminders_interval_hours: int


@dataclass
class Settings:
    bot: BotConfig
    db: DbConfig
    redis: RedisConfig
    yandex_gpt: YandexGPTConfig
    timezone: str
    cron: CronConfig


def get_settings() -> Settings:
    bot = BotConfig(
        token=os.getenv('BOT_TOKEN', ''),
    )
    db = DbConfig(
        url=os.getenv('DB_URL', 'sqlite://db.sqlite3'),
    )
    redis = RedisConfig(
        url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    )
    yandex_gpt = YandexGPTConfig(
        api_key=os.getenv('YANDEX_GPT_API_KEY', ''),
        folder_id=os.getenv('YANDEX_GPT_FOLDER_ID', ''),
        endpoint=os.getenv(
            'YANDEX_GPT_ENDPOINT',
            'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
        ),
    )
    timezone = os.getenv('DEFAULT_TIMEZONE', 'UTC')
    daily_hour = int(os.getenv('DAILY_SUMMARY_HOUR', '23'))
    daily_minute = int(os.getenv('DAILY_SUMMARY_MINUTE', '59'))
    morning_hour = int(os.getenv('MORNING_PLAN_HOUR', '8'))
    morning_minute = int(os.getenv('MORNING_PLAN_MINUTE', '0'))
    weekly_weekday = int(os.getenv('WEEKLY_REPORT_WEEKDAY', '6'))
    weekly_hour = int(os.getenv('WEEKLY_REPORT_HOUR', '23'))
    reminders_interval_hours = int(os.getenv('REMINDERS_INTERVAL_HOURS', '2'))
    cron = CronConfig(
        daily_hour=daily_hour,
        daily_minute=daily_minute,
        morning_hour=morning_hour,
        morning_minute=morning_minute,
        weekly_weekday=weekly_weekday,
        weekly_hour=weekly_hour,
        reminders_interval_hours=reminders_interval_hours,
    )
    return Settings(
        bot=bot,
        db=db,
        redis=redis,
        yandex_gpt=yandex_gpt,
        timezone=timezone,
        cron=cron,
    )
