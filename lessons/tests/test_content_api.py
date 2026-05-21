from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from lessons.models import Course, Lesson, Task


class ContentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            password="StrongPass123",
        )

        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="HSK 1")

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Приветствие",
            description="Базовые фразы приветствия",
        )

        self.task = Task.objects.create(
            lesson=self.lesson,
            title="Произнесите фразу",
            task_description="Скажите: 你好",
        )

    def test_get_courses(self):
        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("courses", response.data)
        self.assertEqual(len(response.data["courses"]), 1)

        self.assertEqual(response.data["courses"][0]["title"], "HSK 1")

    def test_get_lessons_by_course(self):
        response = self.client.get(f"/api/lessons/{self.course.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("lessons", response.data)

        self.assertEqual(len(response.data["lessons"]), 1)

        self.assertEqual(response.data["lessons"][0]["title"], "Приветствие")

    def test_get_tasks_by_lesson(self):
        response = self.client.get(f"/api/tasks/{self.lesson.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("tasks", response.data)

        self.assertEqual(len(response.data["tasks"]), 1)

        self.assertEqual(response.data["tasks"][0]["title"], "Произнесите фразу")
