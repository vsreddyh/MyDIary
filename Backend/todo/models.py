from datetime import date, timedelta
import re
import calendar
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import datetime
from Journal.models import RowEntry

# Create your models here.


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listname = models.CharField(max_length=30, default="Tasks")
    to_journal = models.BooleanField(default=False)


class Task(models.Model):
    PRIORITY_LEVELS = [(i, f"Level {i}") for i in range(1, 11)]

    userData = models.ForeignKey(List, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    original_date = models.CharField(null=True, blank=True, max_length=10)
    name = models.CharField(max_length=50)
    repeat = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    journalid = models.ForeignKey(
        RowEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="taskid",
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="subtask"
    )
    oldestAncestor = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="descendants",
    )
    child = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="parenttask",
    )
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


def month_clamper(year, month, day):
    last_day = calendar.monthrange(year, month)[1]
    day = min(day, last_day)
    return date(year, month, day)


def fix_invalid_date(year, month, day):
    while True:
        days_in_month = calendar.monthrange(year, month)[1]
        if day <= days_in_month:
            return date(year, month, day)
        day -= days_in_month
        month += 1
        if month > 12:
            month = 1
            year += 1


def renewer(repeat, original_date):
    if original_date is None:
        return None, None
    year = int(original_date[0:4])
    month = int(original_date[5:7])
    day = int(original_date[8:10])
    new_original_date = original_date
    new_date = date.today()
    if repeat[-1] == "d":
        new_date = fix_invalid_date(year, month, day) + timedelta(days=repeat[:-1])
        new_original_date = str(new_date)
    elif repeat[-1] == "w":
        new_date = fix_invalid_date(year, month, day) + timedelta(weeks=repeat[:-1])
        new_original_date = str(new_date)
    elif repeat[-1] == "m":
        month = (month + repeat[:-1]) % 12
        year = year + ((month + repeat[:-1]) / 12)
        new_original_date = str(year) + "-" + str(month) + "-" + str(day)
        new_date = month_clamper(year, month, day)
    else:
        year = year + repeat[:-1]
        new_original_date = str(year) + "-" + str(month) + "-" + str(day)
        new_date = month_clamper(year, month, day)
    return new_date, new_original_date


# signals
@receiver(post_save, sender=Task)
def repeat_chain(sender, instance, **kwargs):
    if instance.repeat is not None and instance.child is None and instance.completed:
        oldchain = instance.oldestAncestor
        repeat = oldchain.repeat
        original_date = oldchain.original_date
        new_date, new_original_date = renewer(repeat, original_date)
        newchain = Task.objects.create(
            userData=oldchain.userData,
            date=new_date,
            name=oldchain.name,
            repeat=oldchain.repeat,
            original_date=new_original_date,
            description=oldchain.description,
            priority=oldchain.priority,
            deadline=oldchain.deadline,
        )
        newchain.oldestAncestor = newchain
        newchain.save()
        while oldchain.child is not None:
            oldchain = oldchain.child
            original_date = oldchain.original_date
            new_date, new_original_date = renewer(repeat, original_date)
            newchild = Task.objects.create(
                userData=oldchain.userData,
                date=new_date,
                name=oldchain.name,
                repeat=oldchain.repeat,
                original_date=new_original_date,
                description=oldchain.description,
                priority=oldchain.priority,
                deadline=oldchain.deadline,
                active=False,
                parent=newchain,
                oldestAncestor=newchain.oldestAncestor,
            )
            newchain.child = newchild
            newchain.save()
            newchain = newchild


@receiver(post_save, sender=Task)
def delete_old_completed_tasks(sender, instance, **kwargs):
    if instance.completed:
        user_data = instance.userData
        completed_tasks = Task.objects.filter(
            userData=user_data, completed=True
        ).order_by("completed_at")
        completed_count = completed_tasks.count()
        if completed_count > 30:
            tasks_to_delete = completed_tasks[: completed_count - 20]
            tasks_to_delete.delete()
