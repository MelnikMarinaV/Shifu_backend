from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import re


def is_chinese(text):
    return bool(re.search(r"[\u4e00-\u9fff]", text))


from .models import Course, Lesson, Task, TaskSubmission
from .serializers import (
    RegisterSerializer,
    MeSerializer,
    MeUpdateSerializer,
    CourseSerializer,
    LessonSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
)
from .services.ollama_service import check_text_with_ollama
from .services.whisper_service import transcribe_audio


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

    serializer = LessonSerializer(items, many=True)

    return Response({"lessons": serializer.data})


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
    items = (
        TaskSubmission.objects.filter(user=request.user)
        .order_by("-created_at")
        .select_related("task", "task__lesson", "task__lesson__course")
    )

    return Response({"submissions": TaskSubmissionSerializer(items, many=True).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_submission_ai(request, submission_id):
    submission = get_object_or_404(
        TaskSubmission.objects.select_related(
            "task", "task__lesson", "task__lesson__course"
        ),
        id=submission_id,
        user=request.user,
    )

    if not submission.result_file:
        return Response({"error": "Аудиофайл не найден"}, status=400)

    try:
        submission.ai_status = "processing"
        submission.save(update_fields=["ai_status"])

        audio_path = submission.result_file.path
        transcript = transcribe_audio(audio_path)

        if not transcript:
            transcript = "Не удалось распознать речь."

        submission.transcript = transcript

        # Если ответ НЕ на китайском — сразу 0
        if not is_chinese(transcript):
            submission.ai_score = 0
            submission.ai_feedback = "Ответ должен быть на китайском языке."
            submission.comment = "Неправильный язык"
            submission.ai_status = "done"
            submission.save(
                update_fields=[
                    "transcript",
                    "ai_score",
                    "ai_feedback",
                    "comment",
                    "ai_status",
                ]
            )

            return Response(
                {
                    "message": "Проверка завершена",
                    "audio_path": audio_path,
                    "transcript": submission.transcript,
                    "score": submission.ai_score,
                    "feedback": submission.ai_feedback,
                    "status": submission.ai_status,
                },
                status=200,
            )

        # Если китайский — отправляем в Ollama
        result = check_text_with_ollama(
            transcript=transcript,
            task_text=submission.task.title,
        )

        submission.ai_score = result.get("score")
        submission.ai_feedback = result.get("feedback")
        submission.comment = result.get("short_comment")
        submission.ai_status = "done"
        submission.save(
            update_fields=[
                "transcript",
                "ai_score",
                "ai_feedback",
                "comment",
                "ai_status",
            ]
        )

        return Response(
            {
                "message": "Проверка завершена",
                "audio_path": audio_path,
                "transcript": submission.transcript,
                "score": submission.ai_score,
                "feedback": submission.ai_feedback,
                "status": submission.ai_status,
            },
            status=200,
        )

    except Exception as e:
        submission.ai_status = "error"
        submission.ai_feedback = str(e)
        submission.save(update_fields=["ai_status", "ai_feedback"])

        return Response({"error": str(e)}, status=500)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_submission_view(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id, user=request.user)

    submission.delete()

    return Response({"detail": "Запись удалена"}, status=status.HTTP_204_NO_CONTENT)
