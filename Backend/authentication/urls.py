from django.urls import path
from .views import create_user, delete_user

urlpatterns = [
    path("create-user", create_user, name="create-user"),
    path("delete-user", delete_user, name="delete-user"),
]
