from core.constants import PAGE_SIZE
from core.mixins import OnlyAuthorMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PostForm
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "posts/home.html"
    queryset = Post.objects.select_related(
        "author",
    )
    ordering = "-created_at"
    paginate_by = PAGE_SIZE


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "posts/post_CUD_form.html"
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        post = get_object_or_404(Post, pk=pk)
        return Post.objects.filter(pk=post.pk).select_related("author")


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_CUD_form.html"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = "posts/post_CUD_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "users:profile", kwargs={"username": self.object.author.username}
        )
