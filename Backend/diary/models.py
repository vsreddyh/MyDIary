from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.TextField()
    date = models.DateField()
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
