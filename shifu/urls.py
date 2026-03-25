from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from lessons import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", views.register_view),
    path("api/auth/token/", TokenObtainPairView.as_view()),
    path("api/auth/token/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", views.me_view),
    path("api/courses/", views.courses),
    path("api/lessons/<int:course_id>/", views.lessons),
    path("api/tasks/<int:lesson_id>/", views.tasks),
    path("api/tasks/<int:task_id>/audio/", views.get_audio),
    path("api/tasks/<int:task_id>/upload-audio/", views.upload_audio),
    path("api/my-submissions/", views.my_submissions),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
