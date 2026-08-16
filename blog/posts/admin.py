from django.contrib import admin
from django.utils.html import format_html

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content",
        "author",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "content")
    list_editable = ("author",)
    search_fields = (
        "content__icontains",
        "author",
    )
    list_filter = ("author",)

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "author",
                    "content",
                    "image",
                    "image_preview",
                ),
            },
        ),
    )

    @admin.display(description="Предпросмотр изображения")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="150" '
                'style="object-fit: cover; border-radius: 50%;" />',
                obj.image.url,
            )
        return "Изображение не загружено"
