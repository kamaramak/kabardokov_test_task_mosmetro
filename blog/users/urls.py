from django.urls import path

from .views import UserProfileUpdateView, UserProfileView

app_name = "users"
urlpatterns = [
    path(
        "profile/profile_edit/",
        UserProfileUpdateView.as_view(),
        name="profile_edit",
    ),
    path(
        "profile/<str:username>/",
        UserProfileView.as_view(),
        name="profile",
    ),
]
