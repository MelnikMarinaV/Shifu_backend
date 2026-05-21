from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from lessons.models import (
    Course,
    Lesson,
    Task,
    TaskSubmission,
)


class AIAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            password="StrongPass123",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title="HSK 1"
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Говорение",
            description="Практика устной речи",
        )

        self.task = Task.objects.create(
            lesson=self.lesson,
            title="Скажите 你好",
            task_description="Произнесите приветствие",
        )

        audio_file = SimpleUploadedFile(
            "test_audio.webm",
            b"fake audio content",
            content_type="audio/webm",
        )

        self.submission = TaskSubmission.objects.create(
            user=self.user,
            task=self.task,
            result_file=audio_file,
        )

    @patch("lessons.views.transcribe_audio")
    @patch("lessons.views.check_text_with_ollama")
    def test_ai_check_success(
        self,
        mock_check_text,
        mock_transcribe,
    ):
        mock_transcribe.return_value = "你好"

        mock_check_text.return_value = {
            "score": 95,
            "feedback": "Отличное произношение",
            "short_comment": "Хороший ответ",
        }

        response = self.client.post(
            f"/api/submissions/{self.submission.id}/check-ai/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.submission.refresh_from_db()

        self.assertEqual(
            self.submission.transcript,
            "你好"
        )

        self.assertEqual(
            self.submission.ai_score,
            95
        )

        self.assertEqual(
            self.submission.ai_feedback,
            "Отличное произношение"
        )

        self.assertEqual(
            self.submission.ai_status,
            "done"
        )