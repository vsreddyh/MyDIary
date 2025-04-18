from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.


class DayEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    last_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")


class RowEntry(models.Model):
    day = models.ForeignKey(DayEntry, on_delete=models.CASCADE, related_name="entries")
    time = models.TimeField()
    entry = models.TextField()

    class Meta:
        ordering = ["time"]
