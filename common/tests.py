from django.test import SimpleTestCase
from rest_framework import status

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
                "errors": {
                    "detail": "You are not authorized on this resource",
                },
            },
        )
