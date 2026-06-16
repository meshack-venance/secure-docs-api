from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


def response_body(response):
    return response.json()


@override_settings(ALLOWED_HOSTS=["localhost", "testserver"])
class AccountTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.email = "learner@example.com"
        self.login_url = reverse("authentication:login")
        self.profile_url = reverse("accounts:profile")

    def test_authenticated_user_can_view_profile(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        access_token = response_body(login_response)["data"]["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.profile_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "User fetched successfully")
        self.assertEqual(body["data"]["email"], self.email)

    def test_anonymous_user_cannot_view_profile(self):
        response = self.client.get(self.profile_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])

    def test_superuser_is_created_with_admin_role(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
        )

        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
