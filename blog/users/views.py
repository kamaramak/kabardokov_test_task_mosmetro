from core.constants import PAGE_SIZE
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from posts.models import Post

from .forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("posts:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            subject="Добро пожаловать в Блог Мосметро",
            message=(
                f"Здравствуйте, {self.object.username}!\n\n"
                "Регистрация в Блоге Мосметро успешно завершена."
            ),
            from_email=None,
            recipient_list=[self.object.email],
        )
        return response


class UserProfileView(ListView):
    model = Post
    template_name = "users/profile.html"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs["username"]
        )
        return (
            Post.objects.filter(author=self.profile)
            .select_related("author")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
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
