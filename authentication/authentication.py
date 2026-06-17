import logging

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password


User = get_user_model()
logger = logging.getLogger(__name__)

AUTHENTICATION_FAILED_MESSAGE = "Authentication credentials are invalid"


class SecureDocsJWTAuthentication(JWTAuthentication):
    """Authenticate access tokens against the current database user record."""

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            self._raise_authentication_failed("token_missing_user_id")

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            self._raise_authentication_failed("token_user_not_found", user_id=user_id)

        if api_settings.CHECK_USER_IS_ACTIVE and not user.is_active:
            self._raise_authentication_failed("token_user_inactive", user_id=user_id)

        if user.role not in User.Role.values:
            self._raise_authentication_failed("token_user_invalid_role", user_id=user_id)

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(api_settings.REVOKE_TOKEN_CLAIM) != get_md5_hash_password(
                user.password
            ):
                self._raise_authentication_failed("token_password_changed", user_id=user_id)

        return user

    def _raise_authentication_failed(self, reason, user_id=None):
        logger.warning(
            "JWT authentication rejected",
            extra={
                "reason": reason,
                "user_id": user_id,
            },
        )
        raise AuthenticationFailed(
            AUTHENTICATION_FAILED_MESSAGE,
            code="authentication_failed",
        )
