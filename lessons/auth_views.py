from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


def _serialize_user(user: User) -> dict:
    """Return a minimal public representation of a user."""
    return {"id": user.id, "username": user.username, "email": user.email or ""}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Create a new user account and return public profile data.
    Expected payload: username, email (optional), password, password_confirm.
    """

    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    password = request.data.get("password")
    password_confirm = request.data.get("password_confirm")

    if not username or not password or not password_confirm:
        return Response(
            {"detail": "Имя пользователя и пароли обязательны."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return Response(
            {"detail": "Пароли не совпадают."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Пользователь с таким именем уже существует."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {"detail": "Пользователь с такой почтой уже существует."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(password)
    except ValidationError as exc:
        return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email or "",
        password=password,
    )

    return Response(_serialize_user(user), status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the current authenticated user."""

    return Response(_serialize_user(request.user))
