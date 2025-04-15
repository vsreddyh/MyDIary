# Create your views here.
import json
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from .models import List, Task


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_bylist(request):  # Fetch tasks of a given list
    try:
        listname = request.GET.get("list")
        ordering = request.GET.get("order", "default")
        if ordering == "priority":
            tasks_qs = Task.objects.priority_first()
        else:
            tasks_qs = Task.objects.default_order()
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not listname:
            return JsonResponse({"error": "List parameter is required"}, status=400)

        userData = List.objects.get(user=request.user, listname=listname)
        tasks = tasks_qs.filter(userData=userData, parent=None).values(
            "id",
            "date",
            "name",
            "repeat",
            "description",
            "chain_id",
            "priority",
            "start_time",
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
        ordering = request.GET.get("order", "default")
        if ordering == "priority":
            tasks_qs = Task.objects.priority_first()
        else:
            tasks_qs = Task.objects.default_order()
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not date:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        userLists = List.objects.filter(user=request.user)
        tasks = tasks_qs.filter(userData__in=userLists, date=date, parent=None).values(
            "id",
            "name",
            "userData__listname",
            "repeat",
            "description",
            "chain_id",
            "priority",
            "start_time",
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
            start_time=data.get("start_time"),
            deadline=data.get("deadline"),
        )

        return JsonResponse({"success": "yes"}, status=201)
    except List.DoesNotExist:
        return JsonResponse({"error": "List no found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
