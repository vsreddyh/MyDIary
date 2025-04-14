from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()


class Task(models.Model):
    userData = models.ForeignKey(List, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=20)
    repeat = models.BooleanField(default=False)
    description = models.TextField()
    chain = models.ForeignKey("self", on_delete=models.CASCADE)
    priority = models.IntegerField()
    time = models.TimeField()
    completed = models.BooleanField()
