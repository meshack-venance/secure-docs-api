from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme


class SecureDocsJWTScheme(SimpleJWTScheme):
    target_class = "authentication.authentication.SecureDocsJWTAuthentication"
