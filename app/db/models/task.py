from datetime import date

from tortoise import fields
from tortoise.fields import ForeignKeyRelation
from tortoise.models import Model

from app.db.models.user import User


class TaskStatus:
    PLANNED = 'planned'
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'


class Task(Model):
    id = fields.IntField(pk=True)
    user: ForeignKeyRelation[User] = fields.ForeignKeyField(
        'models.User',
        related_name='tasks',
        on_delete=fields.OnDelete.CASCADE,
    )
    title = fields.CharField(max_length=255)
    planned_seconds = fields.IntField()
    spent_seconds = fields.IntField(default=0)
    date = fields.DateField(default=date.today)
    status = fields.CharField(max_length=16, default=TaskStatus.PLANNED)
    score = fields.IntField(null=True)
    category = fields.CharField(max_length=128, null=True)

    class Meta:
        table = 'task'
