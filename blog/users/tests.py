import io
import tempfile
from datetime import date, timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.registration_url = reverse("registration")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "Test",
            "last_name": "User",
            "bio": "Информация о пользователе",
            "date_of_birth": "2000-01-01",
        }
        self.user = User.objects.create_user(
            username="alice",
            password="pass12345",
            email="alice@example.com",
            bio="Биография пользователя",
        )

    def test_registration_creates_user(self):
        response = self.client.post(self.registration_url, self.user_data)

        self.assertRedirects(response, reverse("posts:home"))
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(str(user.date_of_birth), "2000-01-01")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_registration_sends_welcome_email(self):
        self.client.post(self.registration_url, self.user_data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])
        self.assertIn("Добро пожаловать", mail.outbox[0].subject)

    def test_registration_saves_email_to_file(self):
        with tempfile.TemporaryDirectory() as email_directory:
            with self.settings(
                EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend",
                EMAIL_FILE_PATH=email_directory,
            ):
                self.client.post(self.registration_url, self.user_data)

            email_file = next(Path(email_directory).iterdir())
            email_content = email_file.read_text(encoding="utf-8")

        self.assertIn("test@example.com", email_content)
        self.assertIn("Subject:", email_content)

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            password="pass12345",
            email=self.user_data["email"],
        )

        response = self.client.post(self.registration_url, self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Пользователь с таким email уже существует.",
        )

    def test_registration_rejects_future_birth_date(self):
        data = self.user_data | {
            "username": "future_user",
            "email": "future@example.com",
            "date_of_birth": (date.today() + timedelta(days=1)).isoformat(),
        }

        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("date_of_birth", response.context["form"].errors)

    def test_profile_displays_bio_and_avatar_fallback(self):
        response = self.client.get(
            reverse("users:profile", kwargs={"username": self.user.username})
        )

        self.assertContains(response, self.user.bio)
        self.assertContains(response, "A")

    def test_profile_of_other_user_is_available(self):
        other_user = User.objects.create_user(
            username="bob",
            password="pass12345",
            email="bob@example.com",
            bio="Биография другого пользователя",
        )

        response = self.client.get(
            reverse("users:profile", kwargs={"username": other_user.username})
        )

        self.assertContains(response, other_user.username)
        self.assertContains(response, other_user.bio)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_profile_update_saves_avatar(self):
        image = Image.new("RGB", (20, 20), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        avatar = SimpleUploadedFile(
            "avatar.jpg", image_bytes.getvalue(), content_type="image/jpeg"
        )
        self.client.login(username="alice", password="pass12345")

        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "bio": "Обновленная биография",
                "date_of_birth": "1995-05-05",
                "avatar": avatar,
            },
        )

        self.assertRedirects(
            response,
            reverse("users:profile", kwargs={"username": "alice"}),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.name.startswith("avatars/"))

    def test_profile_update_rejects_future_birth_date(self):
        self.client.login(username="alice", password="pass12345")

        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "bio": "Биография пользователя",
                "date_of_birth": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("date_of_birth", response.context["form"].errors)

    def test_profile_update_rejects_too_long_bio(self):
        self.client.login(username="alice", password="pass12345")

        response = self.client.post(
            reverse("users:profile_edit"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "bio": "a" * 301,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("bio", response.context["form"].errors)

    def test_user_can_log_in(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "pass12345"}
        )

        self.assertRedirects(response, reverse("posts:home"))

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "wrong"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_email_with_reset_link(self):
        response = self.client.post(
            reverse("password_reset"), {"email": "alice@example.com"}
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])
        self.assertIn("/auth/reset/", mail.outbox[0].body)
        self.assertIn("не переходите по ссылке", mail.outbox[0].body)

    def test_user_can_log_out(self):
        self.client.login(username="alice", password="pass12345")

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
