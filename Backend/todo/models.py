from collections import defaultdict
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listname = models.CharField(max_length=30, default="Tasks")


class Task(models.Model):
    userData = models.ForeignKey(List, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=20)
    repeat = models.BooleanField(default=False)
    description = models.TextField()
    parent = models.ForeignKey("self", default=None, on_delete=models.CASCADE)
    chain = models.ForeignKey("self", default=None, on_delete=models.CASCADE)
    priority = models.IntegerField()
    start_time = models.TimeField()
    deadline = models.DateTimeField()
    completed = models.BooleanField()

    class Meta:
        ordering = [
            "-completed",
            "date",
            "start_time",
            "-priority",
        ]
