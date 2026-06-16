from django.urls import path

from authentication.views import LoginView, LogoutView, RefreshTokenView, RegisterView

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
