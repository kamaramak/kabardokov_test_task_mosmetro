from core.constants import PAGE_SIZE
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from posts.models import Post

from .forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("login")


class UserProfileView(ListView):
    model = Post
    template_name = "users/profile.html"
    ordering = "-created_at"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return super().get_queryset().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs["username"]
        context["profile"] = get_object_or_404(User, username=username)
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/profile_edit.html"

    def get_success_url(self):
        return reverse(
            "users:profile", kwargs={"username": self.request.user.username}
        )

    def get_object(self, queryset=None):
        return self.request.user


class CustomLoginView(LoginView):
    template_name = "registration/login.html"


class CustomLogoutView(LogoutView):
    template_name = "registration/logged_out.html"
