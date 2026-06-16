from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        view = renderer_context.get("view")

        if self._should_skip_envelope(data, view):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = getattr(response, "status_code", 200)
        success = status_code < 400

        if success:
            data = {
                "success": True,
                "message": self._get_success_message(view),
                "data": data,
            }
        else:
            data = {
                "success": False,
                "message": self._get_error_message(data),
                "data": None,
                "errors": data,
            }

        return super().render(data, accepted_media_type, renderer_context)

    def _should_skip_envelope(self, data, view):
        if isinstance(data, dict) and {"success", "message", "data"}.issubset(data):
            return True

        view_module = getattr(view.__class__, "__module__", "")
        return view_module.startswith("drf_spectacular")

    def _get_success_message(self, view):
        if not view:
            return "Request processed successfully"

        action = getattr(view, "action", None)
        response_messages = getattr(view, "response_messages", {})

        if action and action in response_messages:
            return response_messages[action]

        return getattr(view, "response_message", "Request processed successfully")

    def _get_error_message(self, data):
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
