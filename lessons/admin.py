from django.contrib import admin
from .models import Course, Lesson, Task, TaskSubmission, UserProfile


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course']
    list_filter = ['course']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'lesson']
    list_filter = ['lesson']


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'task', 'created_at']
    list_filter = ['user', 'task', 'created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']