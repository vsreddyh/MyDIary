from django.urls import path
from .views import (
    add_child,
    alter_date,
    alter_deadline,
    alter_description,
    alter_priority,
    alter_repeat,
    get_tasks_bydate,
    get_tasks_bylist,
    check_task,
    get_overdue_tasks_count,
    delete_entry_from_todo,
    delete_task,
    todo_to_entry,
    get_lists,
    get_task,
    rename,
    set_task,
    uncheck_task,
)

urlpatterns = [
    path("add-child", add_child, name="add_child"),
    path("alter-date", alter_date, name="alter-date"),
    path("alter-deadline", alter_deadline, name="alter-deadline"),
    path("alter-description", alter_description, name="alter-description"),
    path("alter-priority", alter_priority, name="alter-priority"),
    path("alter-repeat", alter_repeat, name="alter-repeat"),
    path("get-tasks-by-date", get_tasks_bydate, name="get-tasks-bydate"),
    path("get-tasks-bylist", get_tasks_bylist, name="get-tasks-bylist"),
    path("check-task", check_task, name="check-task"),
    path(
        "get-overdue-tasks-count",
        get_overdue_tasks_count,
        name="get-overdue-tasks-count",
    ),
    path(
        "delete-entry-from-todo", delete_entry_from_todo, name="delete-entry-from-todo"
    ),
    path("delete-task", delete_task, name="delete-task"),
    path("todo-to-entry", todo_to_entry, name="todo-to-entry"),
    path("get-lists", get_lists, name="get-lists"),
    path("get-task", get_task, name="get-task"),
    path("rename", rename, name="rename"),
    path("set-task", set_task, name="set-task"),
    path("uncheck-task", uncheck_task, name="uncheck-task"),
]
