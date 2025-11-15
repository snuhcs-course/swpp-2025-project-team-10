from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from social.models import Post

User = get_user_model()


class CreatePostTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        self.client.login(
            username="testuser", password="password123"
        )  # authenticate the client
        self.url = "/posts/create/"

    def test_create_post_success(self):
        data = {
            "content": "This is my first post!",
            "post_type": "text",
            "is_public": True,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(
            Post.objects.first().content, "This is my first post!"
        )

    def test_create_post_unauthenticated(self):
        self.client.logout()
        data = {"content": "No login post"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Additional pytest-based tests for post creation

import pytest


@pytest.mark.django_db
def test_create_post_with_invalid_data():
    """Test POST /posts/create/ with invalid data returns 400."""
    from rest_framework.test import APIClient
    
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Missing content
    res = client.post("/posts/create/", {}, format="json")
    assert res.status_code == 400
    assert "error" in res.data or "content" in res.data


@pytest.mark.django_db
def test_home_feed_success():
    """Test home_feed view returns posts."""
    from rest_framework.test import APIClient
    
    client = APIClient()
    user = User.objects.create(username="user_feed", email="ufeed@test.com", first_name="U", last_name="ser")
    
    # Create some public posts
    Post.objects.create(author=user, content="Post 1", is_public=True)
    Post.objects.create(author=user, content="Post 2", is_public=True)
    
    client.force_authenticate(user)
    res = client.get("/home/")
    
    assert res.status_code == 200
    assert "results" in res.data
    assert len(res.data["results"]) >= 2


@pytest.mark.django_db
def test_create_post_with_content_only():
    """Test create_post with just content."""
    from rest_framework.test import APIClient
    
    client = APIClient()
    user = User.objects.create(username="user_post", email="upost@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    res = client.post(
        "/posts/create/",
        {"content": "Test post content"},
        format="json",
    )
    assert res.status_code == 201
    assert "post" in res.data
    assert Post.objects.filter(author=user, content="Test post content").exists()


@pytest.mark.django_db
def test_create_post_with_related_book():
    """Test create_post with related_book."""
    from rest_framework.test import APIClient
    from books.models import Author as BookAuthor, Book, Publisher
    
    client = APIClient()
    user = User.objects.create(username="user_book_post", email="ubpost@test.com", first_name="U", last_name="ser")
    
    publisher = Publisher.objects.create(name="Pub2")
    auth = BookAuthor.objects.create(name="Auth2")
    book = Book.objects.create(
        title="Test Book",
        owner=user,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    client.force_authenticate(user)
    res = client.post(
        "/posts/create/",
        {
            "content": "Post about my book",
            "related_book": book.id,
        },
        format="json",
    )
    assert res.status_code == 201
    
    post = Post.objects.get(author=user, content="Post about my book")
    assert post.related_book == book


@pytest.mark.django_db
def test_create_post_invalid_data():
    """Test creating post with invalid data."""
    from rest_framework.test import APIClient
    
    client = APIClient()
    user = User.objects.create(username="user", email="user@test.com", first_name="U", last_name="ser")
    user.set_password("pass123")
    user.save()
    
    client.force_authenticate(user)
    
    # Missing required content
    res = client.post(
        "/posts/create/",
        {},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_post_empty_content():
    """Test creating post with empty content."""
    from rest_framework.test import APIClient
    
    client = APIClient()
    user = User.objects.create(username="user2", email="user2@test.com", first_name="U", last_name="ser")
    user.set_password("pass123")
    user.save()
    
    client.force_authenticate(user)
    
    res = client.post(
        "/posts/create/",
        {"content": ""},
        format="json",
    )
    assert res.status_code == 400
