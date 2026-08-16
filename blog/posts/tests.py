import io
import tempfile

from core.constants import PAGE_SIZE
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

User = get_user_model()


class PostViewsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", password="pass12345", email="author@example.com"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass12345", email="other@example.com"
        )
        self.post = Post.objects.create(
            author=self.author, content="Исходный текст публикации"
        )

    def test_unauthenticated_user_is_redirected_from_post_creation(self):
        response = self.client.get(reverse("posts:post_CUD_form"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('posts:post_CUD_form')}",
        )

    def test_author_can_create_post(self):
        self.client.login(username="author", password="pass12345")

        response = self.client.post(
            reverse("posts:post_CUD_form"),
            {"content": "Новая публикация автора"},
        )

        post = Post.objects.get(content="Новая публикация автора")
        self.assertEqual(post.author, self.author)
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"pk": post.pk})
        )

    def test_empty_post_content_is_invalid(self):
        self.client.login(username="author", password="pass12345")

        response = self.client.post(
            reverse("posts:post_CUD_form"), {"content": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.context["form"].errors)

    def test_too_short_post_content_is_invalid(self):
        self.client.login(username="author", password="pass12345")

        response = self.client.post(
            reverse("posts:post_CUD_form"), {"content": "Коротко"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.context["form"].errors)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_author_can_create_post_with_image(self):
        image = Image.new("RGB", (20, 20), color="blue")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        self.client.login(username="author", password="pass12345")

        response = self.client.post(
            reverse("posts:post_CUD_form"),
            {
                "content": "Публикация с изображением",
                "image": SimpleUploadedFile(
                    "post.jpg",
                    image_bytes.getvalue(),
                    content_type="image/jpeg",
                ),
            },
        )

        post = Post.objects.get(content="Публикация с изображением")
        self.assertTrue(post.image.name.startswith("post_images/"))
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_update_post(self):
        self.client.login(username="other", password="pass12345")
        url = reverse("posts:update_post", kwargs={"pk": self.post.pk})

        response = self.client.post(url, {"content": "Попытка изменить пост"})

        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Исходный текст публикации")

    def test_unauthenticated_user_is_redirected_from_post_update(self):
        url = reverse("posts:update_post", kwargs={"pk": self.post.pk})
        response = self.client.get(url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={url}",
        )

    def test_author_can_update_and_delete_post(self):
        self.client.login(username="author", password="pass12345")
        update_url = reverse("posts:update_post", kwargs={"pk": self.post.pk})

        response = self.client.post(
            update_url, {"content": "Обновленный текст поста"}
        )

        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"pk": self.post.pk})
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Обновленный текст поста")

        response = self.client.post(
            reverse("posts:delete_post", kwargs={"pk": self.post.pk})
        )

        self.assertRedirects(
            response,
            reverse(
                "users:profile", kwargs={"username": self.author.username}
            ),
        )
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_other_user_cannot_delete_post(self):
        self.client.login(username="other", password="pass12345")

        response = self.client.post(
            reverse("posts:delete_post", kwargs={"pk": self.post.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_unauthenticated_user_is_redirected_from_post_deletion(self):
        url = reverse("posts:delete_post", kwargs={"pk": self.post.pk})

        response = self.client.post(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_post_detail_is_public(self):
        response = self.client.get(
            reverse("posts:post_detail", kwargs={"pk": self.post.pk})
        )

        self.assertContains(response, self.post.content)
        self.assertContains(response, self.author.username)

    def test_post_list_is_paginated(self):
        Post.objects.bulk_create(
            [
                Post(author=self.author, content=f"Публикация номер {number}")
                for number in range(PAGE_SIZE + 5)
            ]
        )

        response = self.client.get(reverse("posts:home"))

        self.assertEqual(len(response.context["page_obj"]), PAGE_SIZE)
        self.assertTrue(response.context["page_obj"].has_next())

        response = self.client.get(f"{reverse('posts:home')}?page=2")

        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertFalse(response.context["page_obj"].has_next())
