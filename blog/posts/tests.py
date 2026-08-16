import tempfile

import pytest
from core.constants import PAGE_SIZE
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from posts.models import Post

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username="author", password="pass", email="author@ex.com"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other", password="pass", email="other@ex.com"
    )


@pytest.fixture
def logged_in_author(client, author):
    client.login(username="author", password="pass")
    return client


@pytest.fixture
def logged_in_other(client, other_user):
    client.login(username="other", password="pass")
    return client


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_post_authenticated(logged_in_author, author):
    """Авторизованный пользователь может создать пост."""
    url = reverse("posts:post_CUD_form")
    image = SimpleUploadedFile(
        "post.jpg", b"content", content_type="image/jpeg"
    )
    response = logged_in_author.post(
        url,
        {
            "content": "Test post content",
        },
        files={"image": image},
    )
    if response.status_code == 200:
        if "form" in response.context:
            print(response.context["form"].errors)
    assert response.status_code == 302
    post = Post.objects.get(content="Test post content")
    assert post.author == author
    assert response.url == reverse("posts:post_detail", kwargs={"pk": post.pk})


@pytest.mark.django_db
def test_create_post_unauthenticated(client):
    """Неавторизованный пользователь перенаправляется на логин."""
    url = reverse("posts:post_CUD_form")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    response = client.post(url, {"content": "Any content"})
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_create_post_empty_content(logged_in_author):
    """Валидация: пустой контент не допускается."""
    url = reverse("posts:post_CUD_form")
    response = logged_in_author.post(url, {"content": ""})
    assert response.status_code == 200
    assert "form" in response.context
    assert "content" in response.context["form"].errors
    assert Post.objects.count() == 0


@pytest.fixture
def existing_post(author):
    return Post.objects.create(author=author, content="Original content")


@pytest.mark.django_db
def test_edit_post_unauthenticated(client, existing_post):
    """Неавторизованный пользователь не может редактировать пост."""
    url = reverse(
        "posts:update_post",
        kwargs={"pk": existing_post.pk},
    )

    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
def test_edit_post_author(logged_in_author, existing_post):
    """Автор может редактировать свой пост."""
    url = reverse("posts:update_post", kwargs={"pk": existing_post.pk})
    response = logged_in_author.post(url, {"content": "Updated content"})
    if response.status_code == 200:
        if "form" in response.context:
            print(response.context["form"].errors)
    assert response.status_code == 302
    assert response.url == reverse(
        "posts:post_detail", kwargs={"pk": existing_post.pk}
    )
    existing_post.refresh_from_db()
    assert existing_post.content == "Updated content"


@pytest.mark.django_db
def test_edit_post_other_user_403(logged_in_other, existing_post):
    """Другой пользователь не может редактировать чужой пост."""
    url = reverse("posts:update_post", kwargs={"pk": existing_post.pk})
    response = logged_in_other.get(url)
    assert response.status_code == 403
    response = logged_in_other.post(url, {"content": "Hacked"})
    assert response.status_code == 403
    existing_post.refresh_from_db()
    assert existing_post.content == "Original content"


@pytest.mark.django_db
def test_delete_post_author(logged_in_author, existing_post):
    """Автор может удалить свой пост."""
    url = reverse("posts:delete_post", kwargs={"pk": existing_post.pk})
    response = logged_in_author.post(url)
    assert response.status_code == 302
    assert response.url == reverse(
        "users:profile", kwargs={"username": existing_post.author.username}
    )
    assert not Post.objects.filter(pk=existing_post.pk).exists()


@pytest.mark.django_db
def test_delete_post_other_user_403(logged_in_other, existing_post):
    """Другой пользователь не может удалить чужой пост."""
    url = reverse("posts:delete_post", kwargs={"pk": existing_post.pk})
    response = logged_in_other.post(url)
    assert response.status_code == 403
    assert Post.objects.filter(pk=existing_post.pk).exists()


@pytest.fixture
def posts_for_pagination(author):
    for i in range(PAGE_SIZE + 5):
        Post.objects.create(author=author, content=f"Test post #{i}")


@pytest.mark.django_db
def test_post_list_pagination(client, posts_for_pagination):
    url = reverse("posts:home")

    response = client.get(url)

    assert response.status_code == 200
    assert "page_obj" in response.context

    page_obj = response.context["page_obj"]

    assert len(page_obj) == PAGE_SIZE
    assert page_obj.has_next()

    assert page_obj.paginator.count == Post.objects.count()
    assert (
        page_obj.paginator.num_pages
        == Post.objects.count() // PAGE_SIZE
        + (1 if Post.objects.count() % PAGE_SIZE else 0)
    )

    response2 = client.get(url + "?page=2")

    assert response2.status_code == 200

    page_obj2 = response2.context["page_obj"]

    assert len(page_obj2) == 5
    assert not page_obj2.has_next()


@pytest.mark.django_db
def test_post_detail_view(client, existing_post):
    """Просмотр отдельного поста доступен всем."""
    url = reverse("posts:post_detail", kwargs={"pk": existing_post.pk})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Original content" in content
    assert existing_post.author.username in content
