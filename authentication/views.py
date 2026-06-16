from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from common.exceptions import SecureDocsException
from authentication.serializers import LogoutSerializer, RegisterSerializer


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
    auth=[],
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
    """Create a user with DRF's generic create flow and the project response wrapper."""

    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    response_message = "User registered successfully"


@extend_schema(
    auth=[],
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
    """Use SimpleJWT's built-in credential check so token behavior stays standard."""

    response_message = "User logged in successfully"


@extend_schema(
    auth=[],
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
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new-refresh",
                },
            },
            response_only=True,
        ),
    ],
)
class RefreshTokenView(TokenRefreshView):
    """Rotate refresh tokens according to SIMPLE_JWT settings in config/settings.py."""

    response_message = "Token refreshed successfully"


@extend_schema(
    summary="Log out user",
    description="Blacklist a refresh token so it cannot be used again.",
    request=LogoutSerializer,
    examples=[
        OpenApiExample(
            "Logout request",
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Logout response",
            value={
                "success": True,
                "message": "User logged out successfully",
                "data": None,
            },
            response_only=True,
        ),
    ],
)
class LogoutView(APIView):
    """Blacklist refresh tokens so logout invalidates future refresh attempts."""

    serializer_class = LogoutSerializer
    response_message = "User logged out successfully"

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # SimpleJWT persists blacklisted tokens when token_blacklist is installed.
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError as exc:
            raise SecureDocsException(
                "Invalid or expired refresh token",
                status_code=status.HTTP_400_BAD_REQUEST,
                error="INVALID_REFRESH_TOKEN",
            ) from exc

        return Response(None, status=status.HTTP_200_OK)
