import json

# Create your views here.
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_redis import get_redis_connection
from .models import DayEntry, RowEntry

CACHE_TTL_SECONDS = 300


@csrf_exempt
@require_http_methods(["GET"])
def get_entries(request):
    redis = get_redis_connection("default")
    date = request.GET.get("date")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    try:
        my_key = f"DiaryApp_{request.user.username}_journalentry_{str(date)}"
        value = redis.json().get(my_key)
        if value is not None:
            redis.expire(my_key, CACHE_TTL_SECONDS)
            return JsonResponse({"success": value.get("entries", {})}, status=200)
        day_entry = DayEntry.objects.get(user=request.user, date=date)
        entries = day_entry.entries.all()
        cache = {}
        for entry in entries:
            entry_data = {
                "id": entry.id,
                "time": entry.time.isoformat(),
                "entry": entry.entry,
            }
            cache[str(entry.id)] = entry_data
        redis.json().set(my_key, "$", {"entries": cache})
        redis.expire(my_key, CACHE_TTL_SECONDS)
        return JsonResponse({"success": cache}, status=200)
    except DayEntry.DoesNotExist:
        return JsonResponse({"success": {}}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def todo_to_entry(date, time, entry, user):
    try:
        redis = get_redis_connection("default")
        if not date:
            return {"error": "Date parameter is required", "status": 400}

        if not time:
            return {"error": "Time parameter is required", "status": 400}

        if not entry:
            return {"error": "Entry parameter is required", "status": 400}

        my_key = f"DiaryApp_{user.username}_journalentry_{str(date)}"
        day_entry, _ = DayEntry.objects.get_or_create(user=user, date=date)
        if redis.json().get(my_key) is None:
            redis.json().set(my_key, "$", {"entries": {}})
        day_entry.last_modified = timezone.now()
        day_entry.save()
        row_entry = RowEntry.objects.create(day=day_entry, time=time, entry=entry)
        path = f"$.entries.{row_entry.id}"
        redis.json().set(
            my_key, path, {"id": row_entry.id, "time": time, "entry": entry}
        )
        redis.expire(my_key, CACHE_TTL_SECONDS)
        return {"success": "New Entry Created", "entry_id": row_entry, "status": 201}
    except Exception as e:
        return {"error": str(e), "status": 500}


def delete_entry_from_todo(user, entry_id):
    try:
        if not entry_id:
            return {"error": "Entry parameter is required", "status": 400}

        entry = RowEntry.objects.get(day__user=user, id=entry_id)
        day_entry = entry.day
        day_entry.last_modified = timezone.now()
        day_entry.save()
        entry.delete()
        return {"success": "Deleted Successfully", "status": 200}
    except RowEntry.DoesNotExist:
        return {"success": "Already Deleted", "status": 200}
    except Exception as e:
        return {"error": str(e), "status": 500}


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def write_entry(request):
    try:
        redis = get_redis_connection("default")
        data = json.loads(request.body)
        date = data.get("date")
        time = data.get("time")
        entry = data.get("entry")
        entry_id = data.get("id")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You don't have authorization"}, status=403)

        if not date:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        if not time:
            return JsonResponse({"error": "Time parameter is required"}, status=400)

        if not entry:
            return JsonResponse({"error": "Entry parameter is required"}, status=400)

        my_key = f"DiaryApp_{request.user.username}_journalentry_{str(date)}"
        day_entry, _ = DayEntry.objects.get_or_create(user=request.user, date=date)
        if redis.json().get(my_key) is None:
            redis.json().set(my_key, "$", {"entries": {}})
        day_entry.last_modified = timezone.now()
        day_entry.save()
        if request.method == "PUT":
            row_entry = RowEntry.objects.get(day=day_entry, id=entry_id)
            row_entry.time = time
            row_entry.entry = entry
            row_entry.save()
            path = f"$.entries.{entry_id}"
            redis.json().set(
                my_key, path, {"id": entry_id, "time": time, "entry": entry}
            )
            redis.expire(my_key, CACHE_TTL_SECONDS)
            return JsonResponse({"success": "Saved Entry"}, status=200)
        row_entry = RowEntry.objects.create(day=day_entry, time=time, entry=entry)
        path = f"$.entries.{row_entry.id}"
        redis.json().set(
            my_key, path, {"id": row_entry.id, "time": time, "entry": entry}
        )
        redis.expire(my_key, CACHE_TTL_SECONDS)
        return JsonResponse({"success": "New Entry Created"}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_entry(request):
    try:
        data = json.loads(request.body)
        entry_id = data.get("id")
        if not entry_id:
            return JsonResponse({"error": "Entry parameter is required"}, status=400)

        entry = RowEntry.objects.get(day__user=request.user, id=entry_id)
        day_entry = entry.day
        day_entry.last_modified = timezone.now()
        day_entry.save()
        entry.delete()
        return JsonResponse({"success": "Deleted Successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def metrics(request):
    end_date = datetime.date.today()
    start_date = request.GET.get("date")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not start_date:
        return JsonResponse({"error": "From Date parameter is required"}, status=400)

    try:
        data = (
            DayEntry.objects.filter(
                user=request.user, date__range=(start_date, end_date)
            )
            .annotate(num_entries=Count("entries"))
            .values("date", "num_entries")
            .order_by("date")
        )
        return JsonResponse({"success": data}, status=200)
    except DayEntry.DoesNotExist:
        return JsonResponse({"success": {}}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
