from rest_framework.response import Response


def success_response(message, data=None, status_code=200):
    """Build a success envelope for the rare cases that bypass the renderer."""
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(message, errors=None, status_code=400):
    """Build an error envelope for manual responses outside DRF exceptions."""
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        },
        status=status_code,
    )
