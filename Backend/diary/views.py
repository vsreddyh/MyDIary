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
