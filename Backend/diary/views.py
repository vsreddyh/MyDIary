import json

# Create your views here.
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from diary.models import Entry


@csrf_exempt
@require_http_methods(["GET"])
def get_entry(request):
    date = request.GET.get("date")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    try:
        entry = Entry.objects.get(user=request.user, date=date)
        return JsonResponse({"success": model_to_dict(entry)}, status=200)
    except Entry.DoesNotExist:
        return JsonResponse({"error": "No entry found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def write_entry(request):
    date = request.GET.get("date")
    title = request.GET.get("titile")
    content = request.GET.get("content")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You don't have authorization"}, status=403)

    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    if not title:
        return JsonResponse({"error": "Title parameter is required"}, status=400)

    if not content:
        return JsonResponse({"error": "Content parameter is required"}, status=400)

    try:
        entry = Entry.objects.get(user=request.user, date=date)
        entry.title = title
        entry.entry = content
        entry.save()
        return JsonResponse({"success": "Saved Entry"}, status=200)
    except Entry.DoesNotExist:
        Entry.objects.create(user=request.user, date=date, title=title, entry=content)
        return JsonResponse({"success": "New Entry Created"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
