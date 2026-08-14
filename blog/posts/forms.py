from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования постов.
    Поля формы:
    - content - текст поста;
    - image - изображение поста.
    """

    class Meta:
        model = Post
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "created_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
