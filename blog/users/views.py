from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = "/login/"


class UserProfileUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user
