from django.urls import path
from .views import (
    create_user,
    delete_user,
    rename_user,
    change_password,
    login_user,
    is_admin,
    has_session,
    logout_user,
)

urlpatterns = [
    path("create-user", create_user, name="create-user"),
    path("delete-user", delete_user, name="delete-user"),
    path("rename-user", rename_user, name="rename-user"),
    path("change-password", change_password, name="change-password"),
    path("login-user", login_user, name="login-user"),
    path("is-admin", is_admin, name="is-admin"),
    path("has-session", has_session, name="has-session"),
    path("logout-user", logout_user, name="logout-user"),
]
