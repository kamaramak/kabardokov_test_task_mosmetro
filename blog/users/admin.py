from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UsAdm

User = get_user_model()


@admin.register(User)
class UserAdmin(UsAdm):
    """Админ-зона для модели CustomUser."""

    list_display = (
        "id",
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


# Добавление дополнительных полей в админ-зону для модели User
UserAdmin.fieldsets += (
    (
        "Дополнительно",
        {
            "fields": (
                "avatar",
                "bio",
                "date_of_birth",
            )
        },
    ),
)
