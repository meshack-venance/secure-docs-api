from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError

from common.exceptions import SecureDocsException, custom_exception_handler


class SecureDocsExceptionTests(SimpleTestCase):
    def test_secure_docs_exception_returns_standard_error_body(self):
        exception = SecureDocsException(
            "You are not authorized on this resource",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
        )

        response = custom_exception_handler(exception, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {
                "success": False,
                "message": "You are not authorized on this resource",
                "status": status.HTTP_401_UNAUTHORIZED,
                "error": "UNAUTHORIZED",
                "data": None,
            },
        )

    def test_validation_error_keeps_field_errors(self):
        exception = ValidationError({"email": ["This field is required."]})

        response = custom_exception_handler(exception, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "email: This field is required.")
        self.assertEqual(response.data["status"], status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data["error"])
        self.assertIsNone(response.data["data"])
        self.assertEqual(str(response.data["errors"]["email"][0]), "This field is required.")
