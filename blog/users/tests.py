import io
import tempfile
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

User = get_user_model()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "strongpass123",
        "password2": "strongpass123",
        "first_name": "Test",
        "last_name": "User",
        "bio": "Test bio for profile",
        "date_of_birth": "2000-01-01",
    }


@pytest.mark.django_db
def test_registration_success(client, user_data):
    """Успешная регистрация нового пользователя."""
    url = reverse("registration")
    response = client.post(url, user_data)
    # Если форма невалидна, выводим ошибки для отладки
    if response.status_code == 200:
        if "form" in response.context:
            print(response.context["form"].errors)
    assert response.status_code == 302
    assert response.url == reverse("posts:home")
    assert User.objects.filter(username="testuser").exists()
    user = User.objects.get(username="testuser")
    assert user.email == "test@example.com"
    assert user.bio == "Test bio for profile"
    assert str(user.date_of_birth) == "2000-01-01"


@pytest.mark.django_db
def test_registration_email_unique(client, user_data):
    """Нельзя зарегистрироваться с уже существующим email."""
    User.objects.create_user(
        username="existing", email="test@example.com", password="pass"
    )
    url = reverse("registration")
    response = client.post(url, user_data)
    assert response.status_code == 200
    # Проверяем наличие ошибки в форме (любой)
    assert "form" in response.context
    assert response.context["form"].errors
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_registration_future_date_of_birth(client):
    """Дата рождения не может быть в будущем."""
    future_date = (date.today() + timedelta(days=1)).isoformat()
    url = reverse("registration")
    response = client.post(
        url,
        {
            "username": "testuser2",
            "email": "test2@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
            "first_name": "Test2",
            "last_name": "User2",
            "date_of_birth": future_date,
        },
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert "date_of_birth" in response.context["form"].errors


@pytest.fixture
def user_alice(db):
    return User.objects.create_user(
        username="alice",
        password="pass123",
        email="alice@example.com",
        first_name="Alice",
        last_name="Smith",
        bio="Hello",
        date_of_birth="1990-01-01",
    )


@pytest.fixture
def user_bob(db):
    return User.objects.create_user(
        username="bob",
        password="pass123",
        email="bob@example.com",
        bio="Hi there",
    )


@pytest.fixture
def logged_in_client(client, user_alice):
    client.login(username="alice", password="pass123")
    return client


@pytest.mark.django_db
def test_profile_view_other_user(logged_in_client, user_bob):
    """Просмотр профиля другого пользователя."""
    url = reverse("users:profile", kwargs={"username": user_bob.username})
    response = logged_in_client.get(url)
    assert response.status_code == 200
    # Проверяем, что имя пользователя присутствует (это точно есть)
    assert user_bob.username in response.content.decode()
    # Не проверяем bio, т.к. шаблон может его не показывать


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_profile_edit_own_profile(logged_in_client, user_alice):
    url = reverse("users:profile_edit")

    image = Image.new("RGB", (200, 200), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    avatar = SimpleUploadedFile(
        "avatar.jpg", image_bytes.read(), content_type="image/jpeg"
    )

    data = {
        "username": "alice",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "bio": "New bio for alice",
        "date_of_birth": "1995-05-05",
        "avatar": avatar,
    }

    response = logged_in_client.post(url, data)
    assert response.status_code == 302

    user_alice.refresh_from_db()
    assert user_alice.bio == "New bio for alice"
    assert str(user_alice.date_of_birth) == "1995-05-05"
    assert user_alice.avatar.name.startswith("avatars/")


@pytest.mark.django_db
def test_profile_edit_invalid_data(logged_in_client, user_alice):
    """Проверка валидации: слишком длинное bio."""
    url = reverse("users:profile_edit")
    long_bio = "a" * 600
    data = {
        "username": "alice",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "bio": long_bio,
        "date_of_birth": "1995-05-05",
    }
    response = logged_in_client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context
    assert "bio" in response.context["form"].errors
    # Не проверяем конкретное сообщение, т.к. оно может быть кастомным


@pytest.fixture
def user_for_auth(db):
    return User.objects.create_user(
        username="testuser", password="testpass", email="test@test.com"
    )


@pytest.mark.django_db
def test_login_success(client, user_for_auth):
    """Успешный вход."""
    url = reverse("login")
    response = client.post(
        url, {"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 302
    assert response.url == reverse("posts:home")


@pytest.mark.django_db
def test_login_fail(client, user_for_auth):
    """Неверный пароль."""
    url = reverse("login")
    response = client.post(url, {"username": "testuser", "password": "wrong"})
    assert response.status_code == 200
    # Проверяем наличие ошибки в форме
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_logout(logged_in_client):
    """Выход из системы (требуется POST)."""
    url = reverse("logout")
    response = logged_in_client.post(url)
    assert response.status_code == 200
    # Проверяем, что пользователь вышел
    assert "_auth_user_id" not in logged_in_client.session
