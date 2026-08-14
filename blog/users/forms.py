from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Форма для регистрации нового пользователя."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "avatar",
            "bio",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return email

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date_of_birth:
            from datetime import date

            if date_of_birth > date.today():
                raise forms.ValidationError(
                    "Дата рождения не может быть позже текущей даты."
                )
        return date_of_birth


class UserUpdateForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "avatar",
            "bio",
        )
