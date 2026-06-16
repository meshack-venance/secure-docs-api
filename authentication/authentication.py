from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


User = get_user_model()


class SecureDocsJWTAuthentication(JWTAuthentication):
    """Authenticate access tokens against the current database user record."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if not user.is_active:
            raise AuthenticationFailed(
                "User account is disabled",
                code="user_inactive",
            )

        if user.role not in User.Role.values:
            raise AuthenticationFailed(
                "User account has an invalid role",
                code="invalid_user_role",
            )

        return user
