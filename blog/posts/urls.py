from django.urls import path

from .views import (
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
)

app_name = "posts"
urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("posts/create/", PostCreateView.as_view(), name="post_CUD_form"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path(
        "posts/<int:pk>/update/", PostUpdateView.as_view(), name="update_post"
    ),
    path(
        "posts/<int:pk>/delete/", PostDeleteView.as_view(), name="delete_post"
    ),
]
