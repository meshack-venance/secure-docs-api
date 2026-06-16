from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import RegisterSerializer, UserSerializer


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
    summary="Register a new user",
    description="Create a Secure Docs user account using email and password.",
    examples=[
        OpenApiExample(
            "Register request",
            value={
                "email": "meshackvenance99@gmail.com",
                "first_name": "Meshack",
                "last_name": "Venance",
                "password": "SecureDocs@2026",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Register response",
            value={
                "success": True,
                "message": "User registered successfully",
                "data": USER_EXAMPLE,
            },
            response_only=True,
        ),
    ],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    response_message = "User registered successfully"


@extend_schema(
    summary="Log in user",
    description="Authenticate with email and password and receive JWT tokens.",
    examples=[
        OpenApiExample(
            "Login request",
            value={
                "email": "meshackvenance99@gmail.com",
                "password": "SecureDocs@2026",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Login response",
            value={
                "success": True,
                "message": "User logged in successfully",
                "data": {
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access",
                },
            },
            response_only=True,
        ),
    ],
)
class LoginView(TokenObtainPairView):
    response_message = "User logged in successfully"


@extend_schema(
    summary="Refresh access token",
    description="Use a refresh token to receive a new access token.",
    examples=[
        OpenApiExample(
            "Refresh request",
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Refresh response",
            value={
                "success": True,
                "message": "Token refreshed successfully",
                "data": {
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new-access",
                },
            },
            response_only=True,
        ),
    ],
)
class RefreshTokenView(TokenRefreshView):
    response_message = "Token refreshed successfully"


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
