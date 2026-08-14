from core.constants import PAGE_SIZE
from django.views.generic import ListView

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    queryset = Post.objects.select_related(
        "author",
    )
    ordering = "-created_at"
    paginate_by = PAGE_SIZE
