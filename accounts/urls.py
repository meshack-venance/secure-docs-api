from django.urls import path

from accounts.views import LoginView, ProfileView, RefreshTokenView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
