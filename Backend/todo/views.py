# Create your views here.
from datetime import date
from django.utils import timezone
import json
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from .models import List, Task


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_bylist(request):  # Fetch tasks of a given list
    try:
        listname = request.GET.get("list")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not listname:
            return JsonResponse({"error": "List parameter is required"}, status=400)

        userData = List.objects.get(user=request.user, listname=listname)
        tasks = Task.objects.filter(userData=userData, parent=None).values(
            "id",
            "date",
            "name",
            "repeat",
            "description",
            "chain_id",
            "priority",
            "deadline",
            "completed",
        )

        return JsonResponse({"success": list(tasks)}, status=200)
    except List.DoesNotExist:
        return JsonResponse({"error": "List no found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_bydate(request):  # Fetch tasks assigned to a given date
    try:
        date = request.GET.get("date")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not date:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        userLists = List.objects.filter(user=request.user)
        tasks = Task.objects.filter(
            userData__in=userLists, date=date, parent=None
        ).values(
            "id",
            "name",
            "userData__listname",
            "repeat",
            "description",
            "chain_id",
            "priority",
            "deadline",
            "completed",
        )
        return JsonResponse({"success": list(tasks)}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_lists(request):  # Fetch lists of given user
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)

        lists = List.objects.filter(user=request.user).values_list(
            "listname", flat=True
        )
        return JsonResponse({"success": list(lists)}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_task(request):  # Fetch a single task
    try:
        taskid = request.GET.get("taskid")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not taskid:
            return JsonResponse({"error": "Task Id parameter is required"}, status=400)

        userLists = List.objects.filter(user=request.user)
        tasks = Task.objects.get(userData__in=userLists, id=taskid)
        return JsonResponse({"success": model_to_dict(tasks)}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_task(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("name") is None:
            return JsonResponse({"error": "Name parameter is required"}, status=400)
        xlist = List.objects.get(
            listname=data.get("listname", "Tasks"), user=request.user
        )

        Task.objects.create(
            userData=xlist,
            date=data.get("date"),
            name=data.get("name"),
            repeat=data.get("repeat"),
            description=data.get("description"),
            priority=data.get("priority"),
            deadline=data.get("deadline"),
        )

        return JsonResponse({"success": "yes"}, status=201)
    except List.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def rename(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("new_name") is None:
            return JsonResponse({"error": "new_name parameter is required"}, status=400)
        if data.get("taskid") is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.name = data.get("new_name")
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def alter_repeat(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("new_repeat") is None:
            return JsonResponse(
                {"error": "new_repeat parameter is required"}, status=400
            )
        if data.get("taskid") is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.repeat = data.get("new_repeat")
        task.full_clean()
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def alter_description(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("new_desc") is None:
            return JsonResponse({"error": "new_desc parameter is required"}, status=400)
        if data.get("taskid") is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.description = data.get("new_desc")
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def add_child(request):
    try:
        data = json.loads(request.body)
        taskid = data.get("taskid")
        child_name = data.get("name")
        child_description = data.get("description")
        child_priority = data.get("priority")
        child_date = data.get("date")
        child_deadline = data.get("deadline")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("child_name") is None:
            return JsonResponse(
                {"error": "child_name parameter is required"}, status=400
            )
        if taskid is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.chain = Task.objects.create(
            userData=task.userData,
            name=child_name,
            date=child_date,
            description=child_description,
            priority=child_priority,
            deadline=child_deadline,
            parent=task,
        )
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def alter_priority(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("priority") is None:
            return JsonResponse({"error": "priority parameter is required"}, status=400)
        if data.get("taskid") is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.priority = data.get("priority")
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def alter_deadline(request):
    try:
        data = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if data.get("deadline") is None:
            return JsonResponse({"error": "Deadline parameter is required"}, status=400)
        if data.get("taskid") is None:
            return JsonResponse({"error": "TaskId parameter is required"}, status=400)

        task = Task.objects.get(userData__user=request.user, id=data.get("taskid"))
        task.deadline = data.get("deadline")
        task.save()
        return JsonResponse({"success": "yes"}, status=200)

    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_overdue_tasks_count(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        overdue_tasks_count = Task.objects.filter(
            Q(userData__user=request.user)
            & (Q(date__lt=date.today()) | Q(deadline__lt=timezone.now()))
        ).count()
        return JsonResponse({"success": overdue_tasks_count}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
