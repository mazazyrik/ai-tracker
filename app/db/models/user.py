from tortoise import fields
from tortoise.models import Model
from tortoise.timezone import now


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    timezone = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(default=now)

    class Meta:
        table = 'user'
