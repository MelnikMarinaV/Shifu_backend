from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Lesson, Task, TaskSubmission
from .serializers import (
    RegisterSerializer,
    MeSerializer,
    MeUpdateSerializer,
    CourseSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {"message": "User created successfully"}, status=status.HTTP_201_CREATED
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def me_view(request):
    if request.method == "GET":
        return Response(MeSerializer(request.user).data)

    serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(MeSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def courses(request):
    items = Course.objects.all()
    return Response({"courses": CourseSerializer(items, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    items = course.lessons.all()

    return Response(
        {
            "lessons": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                }
                for item in items
            ]
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tasks(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    items = lesson.tasks.all()

    return Response(
        {
            "tasks": TaskSerializer(items, many=True).data,
            "description": lesson.description,
            "title": lesson.title,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_audio(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not task.audio_file:
        return Response({"error": "Audio not found"}, status=404)

    return FileResponse(task.audio_file.open("rb"), content_type="audio/mpeg")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_audio(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    audio = request.FILES.get("audio")

    if not audio:
        return Response({"error": "Audio file is required"}, status=400)

    submission = TaskSubmission.objects.create(
        user=request.user,
        task=task,
        result_file=audio,
        comment=request.data.get("comment", ""),
    )

    return Response(
        {
            "message": "Audio uploaded successfully",
            "submission": TaskSubmissionSerializer(submission).data,
        },
        status=201,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_submissions(request):
    items = TaskSubmission.objects.filter(user=request.user).select_related(
        "task", "task__lesson", "task__lesson__course"
    )

    return Response({"submissions": TaskSubmissionSerializer(items, many=True).data})
