from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Course, Lesson, Task, TaskSubmission


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class MeSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="profile.avatar", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "avatar"]


class MeUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="profile.avatar", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "avatar"]
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }

    def update(self, instance, validated_data):
        # --- USER DATA ---
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # --- PROFILE DATA ---
        profile_data = validated_data.get("profile", {})
        avatar = profile_data.get("avatar")

        if avatar:
            instance.profile.avatar = avatar
            instance.profile.save()

        return instance


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title"]


class LessonTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title"]


class LessonSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "course", "tasks"]

    def get_tasks(self, obj):
        tasks = Task.objects.filter(lesson=obj)
        return LessonTaskSerializer(tasks, many=True).data


class TaskSerializer(serializers.ModelSerializer):
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id", "title", "task_description", "lesson", "has_audio"]

    def get_has_audio(self, obj):
        return bool(obj.audio_file)


class TaskSubmissionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)
    lesson_title = serializers.CharField(source="task.lesson.title", read_only=True)
    course_title = serializers.CharField(
        source="task.lesson.course.title", read_only=True
    )

    class Meta:
        model = TaskSubmission
        fields = [
            "id",
            "task",
            "task_title",
            "lesson_title",
            "course_title",
            "comment",
            "result_file",
            "created_at",
            "transcript",
            "ai_feedback",
            "ai_score",
            "ai_status",
        ]
