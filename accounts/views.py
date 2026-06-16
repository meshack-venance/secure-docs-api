from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics

from accounts.serializers import UserSerializer


USER_EXAMPLE = {
    "id": 1,
    "email": "meshackvenance99@gmail.com",
    "first_name": "Meshack",
    "last_name": "Venance",
    "role": "USER",
    "is_active": True,
    "date_joined": "2026-06-16T10:00:00Z",
}


@extend_schema(
    summary="Get current user profile",
    description="Return the authenticated user's profile.",
    examples=[
        OpenApiExample(
            "Profile response",
            value={
                "success": True,
                "message": "User fetched successfully",
                "data": USER_EXAMPLE,
            },
            response_only=True,
        ),
    ],
)
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    response_message = "User fetched successfully"

    def get_object(self):
        return self.request.user
