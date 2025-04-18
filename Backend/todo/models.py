from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import time
import re
from django.core.exceptions import ValidationError

# Create your models here.


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listname = models.CharField(max_length=30, default="Tasks")
    to_journal = models.BooleanField(default=False)


class Task(models.Model):
    PRIORITY_LEVELS = [(i, f"Level {i}") for i in range(1, 11)]

    userData = models.ForeignKey(List, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=50)
    repeat = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subtask"
    )
    chain = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="parenttask",
    )  # child tasks
    priority = models.IntegerField(default=5, choices=PRIORITY_LEVELS)
    deadline = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateField(null=True, blank=True)

    def clean(self):
        if self.repeat:
            if not re.match(r"^\d+[dwmy]$", self.repeat):
                raise ValidationError(
                    "Repeat should be in the format of 'Xd' or 'Xw', where X is a number."
                )

    class Meta:
        ordering = ["completed", "date", "-priority", "deadline"]
        indexes = [
            models.Index(fields=["userData"]),
            models.Index(fields=["date"]),
            models.Index(fields=["completed"]),
            models.Index(fields=["priority"]),
        ]


# signals
@receiver(post_save, sender=Task)
def delete_old_completed_tasks(sender, instance, **kwargs):
    if instance.completed:
        user_data = instance.userData
        completed_tasks = Task.objects.filter(
            userData=user_data, completed=True
        ).order_by("completed_at")
        completed_count = completed_tasks.count()
        if completed_count > 20:
            tasks_to_delete = completed_tasks[: completed_count - 20]
            tasks_to_delete.delete()
