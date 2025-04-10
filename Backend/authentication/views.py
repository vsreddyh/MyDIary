import json

# Create your views here.
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=500)
        if not password:
            return JsonResponse({"error": "Password is required"}, status=500)

        is_first_user = User.objects.count() == 0

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=403)

        user = User.objects.create_user(username=username, password=password)

        if is_first_user:
            user.is_staff = True
            user.is_superUser = True
            user.save()
            return JsonResponse(
                {"success": "Created Succesfully", "admin": is_first_user},
                status=201,
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=500)

        user = User.objects.filter(username=username).first()

        # if user.is_staff:
        #   return JsonResponse({"error": "Admin cannot be Deleted"}, status=500)

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        user.delete()
        return JsonResponse({"success": f"User '{username}' deleted"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def rename_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        newusername = data.get("newusername")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=500)

        if not newusername:
            return JsonResponse({"error": "Username is required"}, status=500)

        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({"error": "Username is required"}, status=500)

        if User.objects.filter(username=newusername):
            return JsonResponse({"error": "Username is already taken"}, status=500)

        user.username = newusername
        user.save()

        return JsonResponse({"success": "Renamed Successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
