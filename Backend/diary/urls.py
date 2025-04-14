from django.urls import path
from .views import get_entry, write_entry

urlpatterns = [
    path("get-entry", get_entry, name="get-entry"),
    path("write-entry", write_entry, name="write-entry"),
]
