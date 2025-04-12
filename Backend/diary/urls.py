from django.urls import path
from .views import (
    get_entry,
)

urlpatterns = [
    path("get-entry", get_entry, name="get-entry"),
]
