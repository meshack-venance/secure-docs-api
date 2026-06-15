from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


@override_settings(ALLOWED_HOSTS=["localhost", "testserver"])
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.email = "learner@example.com"
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")

    def test_user_can_register(self):
        response = self.client.post(
            self.register_url,
            {
                "email": self.email,
                "first_name": "Secure",
                "last_name": "Learner",
                "password": self.password,
            },
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.email).exists())
        self.assertNotIn("password", response.data)

    def test_user_can_log_in(self):
        User.objects.create_user(email=self.email, password=self.password)

        response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authenticated_user_can_view_profile(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        access_token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.profile_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)

    def test_anonymous_user_cannot_view_profile(self):
        response = self.client.get(self.profile_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_is_created_with_admin_role(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
        )

        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
