from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from core.forms import UserBaseForm, UserCleanBaseForm

User = get_user_model()


class UserCreateForm(UserCleanBaseForm, UserCreationForm):
    """Форма для регистрации нового пользователя."""

    pass


class UserUpdateForm(UserCleanBaseForm):
    """Форма для редактирования профиля пользователя."""

    pass


class UserProfileForm(UserBaseForm):
    """Форма для отображения профиля пользователя."""

    pass
