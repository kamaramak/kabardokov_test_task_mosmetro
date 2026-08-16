from django.contrib.auth.forms import UserCreationForm

from .base_forms import UserCleanBaseForm


class UserRegistrationForm(UserCleanBaseForm, UserCreationForm):
    """Форма для регистрации нового пользователя."""



class UserUpdateForm(UserCleanBaseForm):
    """Форма для редактирования профиля пользователя."""
