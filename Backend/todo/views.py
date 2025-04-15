# Create your views here.
import json
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import List, Task


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_bylist(request):
    try:
        listname = request.GET.get("list")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not listname:
            return JsonResponse({"error": "List parameter is required"}, status=400)

        userData = List.objects.get(user=request.user, listname=listname)
        tasks = Task.objects.filter(userData=userData,parent=None).values(
            "id",
            "date",
            "name",
            "repeat",
            "listname",
            "description",
            "chain",
            "priority",
            "start_time",
            "deadline",
            "completed",
        )
        return JsonResponse({"success": tasks}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        userLists = List.objects.filter(user=request.user)
        tasks = Task.objects.filter(userData__in=userLists,parent=None).values(
            "id",
            "name",
            "userData__listname",
            "repeat",
            "description",
            "chain",
            "priority",
            "start_time",
            "deadline",
            "completed",
        )
        return JsonResponse({"success": tasks}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_bydate(request):
    try:
        date = request.GET.get("date")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not date:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        userLists = List.objects.filter(user=request.user)
        tasks = Task.objects.filter(userData__in=userLists date=date,parent=None).values(
            "id",
            "name",
            "userData__listname",
            "repeat",
            "description",
            "chain",
            "priority",
            "start_time",
            "deadline",
            "completed",
        )
        return JsonResponse({"success": tasks}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_lists(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)

        lists = List.objects.filter(user=request.user).values("listname")
        return JsonResponse({"success": lists}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_task(request):
    try:
        taskid = request.GET.get("taskid")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)
        if not taskid:
            return JsonResponse({"error": "Task Id parameter is required"}, status=400)

        userLists = List.objects.filter(user=request.user)
        tasks = Task.objects.filter(userData__in=userLists date=date).values(
            "id",
            "name",
            "userData__listname",
            "repeat",
            "description",
            "chain",
            "priority",
            "start_time",
            "deadline",
            "completed",
        )
        return JsonResponse({"success": tasks}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

