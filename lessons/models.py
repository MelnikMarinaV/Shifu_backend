from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default="", blank=True, null=True)
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=200)
    lesson = models.ForeignKey(Lesson, related_name="tasks", on_delete=models.CASCADE)
    task_description = models.TextField(default="")
    audio_file = models.FileField(upload_to="task_audio/", blank=True, null=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.user.username


class TaskSubmission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="task_submissions",
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(Task, related_name="submissions", on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True, default="")
    result_file = models.FileField(upload_to="submissions/")
    created_at = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(blank=True, null=True)
    ai_feedback = models.TextField(blank=True, null=True)
    ai_score = models.IntegerField(blank=True, null=True)
    ai_status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"{self.user.username} -> {self.task.title}"
