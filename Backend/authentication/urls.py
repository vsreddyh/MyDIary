from django.urls import path
from .views import create_user, delete_user, rename_user

urlpatterns = [
    path("create-user", create_user, name="create-user"),
    path("delete-user", delete_user, name="delete-user"),
    path("rename-user", rename_user, name="rename-user"),
]
