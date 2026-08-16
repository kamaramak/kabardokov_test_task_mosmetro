from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UsAdm
from django.utils.html import format_html

from .models import CustomUser as User


@admin.register(User)
class UserAdmin(UsAdm):
    """Админ-зона для модели CustomUser."""

    list_display = (
        "id",
        "avatar_thumbnail",
        "username",
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
    )

    list_display_links = ("id", "username")

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
    )

    readonly_fields = (
        "avatar_preview",
    )

    @admin.display(description="Аватар")
    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "—"

    @admin.display(description="Предпросмотр аватара")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="150" height="150" '
                'style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "Аватар не загружен"


UserAdmin.fieldsets += (
        (
            "Дополнительно",
            {
                "fields": (
                    "avatar",
                    "avatar_preview",
                    "bio",
                    "date_of_birth",
                ),
            },
        ),
    )
