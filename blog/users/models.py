from core.constants import MAX_BIO_LENGTH, MIN_BIO_LENGTH
from core.validators import validate_avatar_size
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class CustomUser(AbstractUser):
    """
    Кастомная модель для работы с пользователем.
    Дополнительно к стандартным полям модели пользователя, добавлены поля:
    - avatar - аватар пользователя;
    - bio - краткая информация о пользователе;
    - date_of_birth - дата рождения пользователя.
    """

    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        default=None,
        verbose_name="Аватар",
        validators=(validate_avatar_size,),
    )
    bio = models.TextField(
        null=True,
        default=None,
        verbose_name="О себе",
        validators=[
            MinLengthValidator(MIN_BIO_LENGTH),
            MaxLengthValidator(MAX_BIO_LENGTH),
        ],
    )
    date_of_birth = models.DateField(
        null=True, default=None, verbose_name="Дата рождения"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
