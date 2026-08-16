from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from users.views import UserRegisterView

handler403 = "pages.views.permission_denied"
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"

urlpatterns = [
    path("", include("posts.urls", namespace="posts")),
    path("admin/", admin.site.urls),
    path("pages/", include("pages.urls", namespace="pages")),
    path("users/", include("users.urls", namespace="users")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        "auth/registration/",
        UserRegisterView.as_view(),
        name="registration",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
