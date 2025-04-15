import json

# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from todo.models import List


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)
        if not password:
            return JsonResponse({"error": "Password is required"}, status=400)

        is_first_user = User.objects.count() == 0

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=409)

        if is_first_user or request.user.is_staff:
            user = User.objects.create_user(username=username, password=password)

            if is_first_user:
                user.is_staff = True
                user.is_superuser = True
                user.save()
            List.objects.create(user=user, listname="Tasks")
            return JsonResponse(
                {"success": "Created Successfully", "admin": is_first_user},
                status=201,
            )
        return JsonResponse({"error": "Not authorized for operation"}, status=403)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        user = User.objects.filter(username=username).first()

        # if user.is_staff:
        #   return JsonResponse({"error": "Admin cannot be Deleted"}, status=500)

        # if not request.user.is_authenticated or not request.user.is_staff:
        #   return JsonResponse({"error": "You don't have authorization for deleting"}, status=403)

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
            return JsonResponse({"error": "Username is required"}, status=400)

        if not newusername:
            return JsonResponse({"error": "New Username is required"}, status=400)

        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({"error": "User not found"}, status=403)

        # if user.is_staff:
        #   return JsonResponse({"error": "Admin cannot be Renamed"}, status=500)

        # if not request.user.is_authenticated or not request.user.is_staff:
        #   return JsonResponse({"error": "You don't have authorization for renaming"}, status=403)

        if User.objects.filter(username=newusername).exists():
            return JsonResponse({"error": "Username is already taken"}, status=409)

        user.username = newusername
        user.save()

        return JsonResponse({"success": "Renamed Successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def change_password(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        newpassword = data.get("newpassword")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        if not newpassword:
            return JsonResponse({"error": "New Password is required"}, status=400)

        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({"error": "User not found"}, status=403)

        # if user.is_staff:
        #   return JsonResponse({"error": "Admin's password cannot be changed"}, status=500)

        # if not request.user.is_authenticated or not request.user.is_staff:
        #   return JsonResponse({"error": "You don't have authorization for changing passwords"}, status=403)

        user.set_password(newpassword)
        user.save()

        return JsonResponse({"success": "Password Changed Successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        if not password:
            return JsonResponse({"error": "Password is required"}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Creates session
            return JsonResponse({"success": "Logged in successfully"}, status=200)

        return JsonResponse({"error": "Invalid credentials"}, status=403)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def is_admin(request):
    try:
        if request.user.is_authenticated:
            return JsonResponse({"success": request.user.is_staff}, status=200)

        return JsonResponse({"success": False}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def has_session(request):
    try:
        if request.user and request.user.is_authenticated:
            return JsonResponse({"success": True}, status=200)

        return JsonResponse({"success": False}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_user(request):
    try:
        logout(request)
        return JsonResponse({"success": "Logged out successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
