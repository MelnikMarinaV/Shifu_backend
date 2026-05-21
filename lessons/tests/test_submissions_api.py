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


class SubmissionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            password="StrongPass123",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="HSK 1")

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Аудирование",
            description="Задания на восприятие речи",
        )

        self.task = Task.objects.create(
            lesson=self.lesson,
            title="Аудиоответ",
            task_description="Запишите ответ",
        )

    def test_upload_audio_answer(self):
        audio_file = SimpleUploadedFile(
            "test_audio.webm",
            b"fake audio content",
            content_type="audio/webm",
        )

        response = self.client.post(
            f"/api/tasks/{self.task.id}/upload-audio/",
            {
                "audio": audio_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            TaskSubmission.objects.filter(
                user=self.user,
                task=self.task,
            ).exists()
        )

    def test_get_my_submissions(self):
        TaskSubmission.objects.create(
            user=self.user,
            task=self.task,
        )

        response = self.client.get("/api/my-submissions/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "submissions",
            response.data,
        )

    def test_delete_submission(self):
        submission = TaskSubmission.objects.create(
            user=self.user,
            task=self.task,
        )

        response = self.client.delete(f"/api/submissions/{submission.id}/delete/")

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(TaskSubmission.objects.filter(id=submission.id).exists())
