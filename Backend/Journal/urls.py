from django.urls import path
from .views import get_entries, write_entry, delete_entry, metrics

urlpatterns = [
    path("get-entries", get_entries, name="get-entries"),
    path("write-entry", write_entry, name="write-entry"),
    path("delete-entry", delete_entry, name="delete-entry"),
    path("metrics", metrics, name="metrics"),
]
