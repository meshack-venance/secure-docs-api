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
        self.refresh_url = reverse("authentication:refresh")
        self.logout_url = reverse("authentication:logout")
        self.profile_url = reverse("accounts:profile")

    def login_user(self, user):
        response = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        return response_body(response)["data"]

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

    def test_valid_access_token_uses_database_user(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        tokens = self.login_user(user)

        response = self.client.get(
            self.profile_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["email"], self.email)

    def test_deleted_user_cannot_use_old_access_token(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        tokens = self.login_user(user)
        user.delete()

        response = self.client.get(
            self.profile_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "User not found")
        self.assertIsNone(body["data"])

    def test_inactive_user_cannot_use_old_access_token(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        tokens = self.login_user(user)
        user.is_active = False
        user.save(update_fields=("is_active",))

        response = self.client.get(
            self.profile_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "User is inactive")
        self.assertIsNone(body["data"])

    def test_user_with_invalid_database_role_cannot_use_access_token(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        tokens = self.login_user(user)
        User.objects.filter(id=user.id).update(role="INVALID")

        response = self.client.get(
            self.profile_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "User account has an invalid role")
        self.assertIsNone(body["data"])

    def test_refresh_token_rotation_returns_new_refresh_token(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        refresh_token = response_body(login_response)["data"]["refresh"]

        response = self.client.post(
            self.refresh_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {refresh_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Token refreshed successfully")
        self.assertIn("access", body["data"])
        self.assertIn("refresh", body["data"])
        self.assertNotEqual(body["data"]["refresh"], refresh_token)

    def test_old_refresh_token_cannot_be_reused_after_rotation(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        refresh_token = response_body(login_response)["data"]["refresh"]

        self.client.post(
            self.refresh_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {refresh_token}",
        )
        response = self.client.post(
            self.refresh_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {refresh_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])

    def test_refresh_token_must_be_sent_as_bearer_header(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        refresh_token = response_body(login_response)["data"]["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Refresh token is required")
        self.assertEqual(body["error"], "REFRESH_TOKEN_REQUIRED")
        self.assertIsNone(body["data"])
        self.assertNotIn("errors", body)

    def test_refresh_token_rejects_malformed_authorization_header(self):
        response = self.client.post(
            self.refresh_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION="Token invalid-refresh-token",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Refresh token must be sent as a Bearer token")
        self.assertEqual(body["error"], "INVALID_REFRESH_AUTH_HEADER")
        self.assertIsNone(body["data"])
        self.assertNotIn("errors", body)

    def test_authenticated_user_can_logout_with_refresh_token(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        tokens = response_body(login_response)["data"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "User logged out successfully")
        self.assertIsNone(body["data"])

    def test_logged_out_refresh_token_cannot_be_used_again(self):
        User.objects.create_user(email=self.email, password=self.password)
        login_response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        tokens = response_body(login_response)["data"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            format="json",
            HTTP_HOST="localhost",
        )
        response = self.client.post(
            self.refresh_url,
            HTTP_HOST="localhost",
            HTTP_AUTHORIZATION=f"Bearer {tokens['refresh']}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])

    def test_anonymous_user_cannot_logout(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": "fake-token"},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])
