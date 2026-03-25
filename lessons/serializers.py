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
        fields = ["avatar"]

    def update(self, instance, validated_data):
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


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "course"]


class TaskSerializer(serializers.ModelSerializer):
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id", "title", "task_description", "lesson", "has_audio"]

    def get_has_audio(self, obj):
        return bool(obj.audio_file)


class TaskSubmissionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = TaskSubmission
        fields = ["id", "task", "task_title", "comment", "result_file", "created_at"]
