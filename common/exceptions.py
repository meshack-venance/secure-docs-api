from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    response.data = {
        "success": False,
        "message": _get_error_message(response.data),
        "data": None,
        "errors": response.data,
    }
    return response


def _get_error_message(data):
    if isinstance(data, dict):
        detail = data.get("detail")
        if detail:
            return str(detail)

        first_key = next(iter(data), None)
        if first_key:
            return f"{first_key}: {data[first_key]}"

    if isinstance(data, list) and data:
        return str(data[0])

    return "Request failed"
