from datetime import timedelta

from core.constants import MAX_BIO_LENGTH, MIN_BIO_LENGTH
from core.validators import validate_image_size
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models


class Post(models.Model):
    """
    Модель для работы с постами.
    Поля модели:
    - author - автор поста;
    - content - текст поста;
    - created_at - время создания поста;
    - updated_at - время последнего обновления поста;
    - image - изображение поста.
    """

    author = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    content = models.TextField(
        verbose_name="Текст поста",
        validators=[
            MinLengthValidator(MIN_BIO_LENGTH),
            MaxLengthValidator(MAX_BIO_LENGTH),
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )
    image = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True,
        default=None,
        verbose_name="Изображение",
        validators=(validate_image_size,),
    )

    def __str__(self):
        return f"Пост {self.id} от {self.author.username}"

    @property
    def was_updated(self):
        return self.updated_at - self.created_at > timedelta(seconds=1)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
