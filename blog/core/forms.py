from datetime import date

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBaseForm(forms.ModelForm):
    """Базовая форма для работы с профилем пользователя."""

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


class UserCleanBaseForm(UserBaseForm):
    """Базовая форма с валидацией полей профиля пользователя."""

    def clean_email(self):
        email = self.cleaned_data.get("email")

        queryset = User.objects.filter(email=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует."
            )

        return email

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")

        if date_of_birth and date_of_birth > date.today():
            raise forms.ValidationError(
                "Дата рождения не может быть позже текущей даты."
            )

        return date_of_birth
