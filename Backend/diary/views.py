import json

# Create your views here.
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from .models import Entry
from django.core.cache import cache


@csrf_exempt
@require_http_methods(["GET"])
def get_entry(request):
    date = request.GET.get("date")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    try:
        my_key = "DiaryApp_" + request.user.username + "_diaryentry_" + str(date)
        value = cache.get(my_key)
        if value is not None:
            return JsonResponse({"success": value}, status=200)
        entry = Entry.objects.get(user=request.user, date=date)
        entry_data = model_to_dict(entry)
        cache.set(my_key, entry_data, timeout=60 * 60)
        return JsonResponse({"success": entry_data}, status=200)
    except Entry.DoesNotExist:
        return JsonResponse({"error": "No entry found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def write_entry(request):
    data = json.loads(request.body)
    date = data.get("date")
    content = data.get("content")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    if not content:
        return JsonResponse({"error": "Content parameter is required"}, status=400)

    my_key = "DiaryApp_" + request.user.username + "_diaryentry_" + str(date)
    entry_data = {"entry": content, "date": date}
    try:
        entry = Entry.objects.create(user=request.user, date=date)
        entry.entry = content
        entry.save()
        cache.set(my_key, entry_data, timeout=60 * 60)
        return JsonResponse({"success": "Saved Entry"}, status=200)
    except Entry.DoesNotExist:
        Entry.objects.create(user=request.user, date=date, entry=content)
        cache.set(my_key, entry_data, timeout=60 * 60)
        return JsonResponse({"success": "New Entry Created"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
