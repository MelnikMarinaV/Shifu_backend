from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthAPITestCase(APITestCase):
    def test_user_registration_success(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
        }

        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_user_registration_password_mismatch(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123",
            "password_confirm": "WrongPass123",
        }

        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="testuser").exists())
        self.assertIn("password_confirm", response.data)

    def test_user_login_success(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
        )

        data = {
            "username": "testuser",
            "password": "StrongPass123",
        }

        response = self.client.post("/api/auth/token/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_wrong_password(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
        )

        data = {
            "username": "testuser",
            "password": "WrongPass123",
        }

        response = self.client.post("/api/auth/token/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_without_token(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_with_token(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
