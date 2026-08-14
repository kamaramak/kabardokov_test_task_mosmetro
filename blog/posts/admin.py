from django.contrib import admin

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
