from tortoise import fields
from tortoise.fields import ForeignKeyRelation
from tortoise.models import Model
from tortoise.timezone import now

from app.db.models.task import Task


class ActiveTimer(Model):
    id = fields.IntField(pk=True)
    task: ForeignKeyRelation[Task] = fields.ForeignKeyField(
        'models.Task',
        related_name='active_timers',
        on_delete=fields.OnDelete.CASCADE,
    )
    started_at = fields.DatetimeField(default=now)
    accumulated_seconds = fields.IntField(default=0)

    class Meta:
        table = 'active_timer'


