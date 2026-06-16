from django.urls import path

from accounts.views import ProfileView

app_name = "accounts"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
]
