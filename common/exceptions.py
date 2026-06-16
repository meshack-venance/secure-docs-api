from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class SecureDocsException(APIException):
    """Project-level exception for business rules that should reach the API."""

    status_code = 400
    default_detail = "Request failed"
    default_code = "bad_request"

    def __init__(self, message=None, status_code=None, error=None):
        if status_code is not None:
            self.status_code = status_code

        self.message = message or self.default_detail
        self.error = error
        super().__init__(detail=self.message, code=self.default_code)


def custom_exception_handler(exc, context):
    """Convert DRF exceptions into the same error envelope clients always expect."""
    response = exception_handler(exc, context)

    if response is None:
        return response

    errors = response.data
    message = _get_error_message(errors)
    error = getattr(exc, "error", None)

    response.data = {
        "success": False,
        "message": message,
        "status": response.status_code,
        "error": error,
        "data": None,
    }
    if not isinstance(exc, SecureDocsException):
        response.data["errors"] = errors

    return response


def _get_error_message(data):
    if isinstance(data, dict):
        detail = data.get("detail")
        if detail:
            return str(detail)

        first_key = next(iter(data), None)
        if first_key:
            return f"{first_key}: {_stringify_error(data[first_key])}"

    if isinstance(data, list) and data:
        return _stringify_error(data)

    return "Request failed"


def _stringify_error(error):
    if isinstance(error, dict):
        first_key = next(iter(error), None)
        if first_key:
            return _stringify_error(error[first_key])

    if isinstance(error, list) and error:
        return _stringify_error(error[0])

    return str(error)
