from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    response_message = "User registered successfully"


class LoginView(TokenObtainPairView):
    response_message = "User logged in successfully"


class RefreshTokenView(TokenRefreshView):
    response_message = "Token refreshed successfully"


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    response_message = "User fetched successfully"

    def get_object(self):
        return self.request.user
