from core.constants import MAX_AVATAR_SIZE, MAX_IMAGE_SIZE
from django.core.exceptions import ValidationError


def validate_image_size(image):
    """Проверка размера изображения для поста."""

    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError("Размер изображения не должен превышать 10 МБ.")


def validate_avatar_size(avatar):
    """Проверка размера аватара пользователя."""

    if avatar.size > MAX_AVATAR_SIZE:
        raise ValidationError("Размер аватара не должен превышать 5 МБ.")
