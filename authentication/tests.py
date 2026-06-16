from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


def response_body(response):
    return response.json()


@override_settings(ALLOWED_HOSTS=["localhost", "testserver"])
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.email = "learner@example.com"
        self.register_url = reverse("authentication:register")
        self.login_url = reverse("authentication:login")

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
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "User registered successfully")
        self.assertTrue(User.objects.filter(email=self.email).exists())
        self.assertNotIn("password", body["data"])

    def test_user_can_log_in(self):
        User.objects.create_user(email=self.email, password=self.password)

        response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "User logged in successfully")
        self.assertIn("access", body["data"])
        self.assertIn("refresh", body["data"])
