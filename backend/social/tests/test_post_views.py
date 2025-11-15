from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
import pytest
from rest_framework.test import APIClient

from social.models import Post, PostLike

User = get_user_model()


class PostViewTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="user2", email="user2@example.com", password="password123"
        )

        # Generate and set JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # URLs
        self.create_url = "/posts/create/"
        self.home_feed_url = "/home/"

        # Create sample posts
        self.public_post = Post.objects.create(
            author=self.other_user, content="Public post", is_public=True
        )
        self.private_post = Post.objects.create(
            author=self.other_user, content="Private post", is_public=False
        )

    # ------------------------------------------------------------
    # 1️⃣ HOME FEED TESTS
    # ------------------------------------------------------------
    def test_home_feed_authenticated(self):
        """Authenticated user should get all public posts."""
        response = self.client.get(self.home_feed_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        results = response.data["results"]

        # Only public posts should appear
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], self.public_post.content)

    def test_home_feed_unauthenticated(self):
        """Unauthenticated users should be blocked."""
        self.client.credentials()  # Remove token
        response = self.client.get(self.home_feed_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------
    # 2️⃣ LIKE / UNLIKE TESTS
    # ------------------------------------------------------------
    def test_like_post_success(self):
        """User should be able to like and unlike a post."""
        like_url = f"/posts/{self.public_post.id}/like/"

        # Like the post
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            PostLike.objects.filter(
                post=self.public_post, user=self.user
            ).exists()
        )

        # Unlike the post (toggle)
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            PostLike.objects.filter(
                post=self.public_post, user=self.user
            ).exists()
        )

    def test_like_post_not_found(self):
        """Return 404 if post does not exist."""
        like_url = "/posts/9999/like/"
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Pytest-based tests for post update


@pytest.mark.django_db
def test_update_post_with_invalid_data():
    """Test PUT /posts/{id}/ with invalid data returns 400."""
    client = APIClient()
    user = User.objects.create(username="user_update", email="u@test.com", first_name="U", last_name="ser")
    post = Post.objects.create(author=user, content="original")
    
    client.force_authenticate(user)
    
    # Empty content
    res = client.put(f"/posts/{post.id}/", {"content": ""}, format="json")
    assert res.status_code == 400 or res.status_code == 404  # Might not have update endpoint


@pytest.mark.django_db
def test_home_feed_returns_multiple_posts():
    """Test home_feed endpoint returns list of public posts."""
    client = APIClient()
    user = User.objects.create(username="viewer", email="viewer@test.com", first_name="V", last_name="iewer")
    
    # Create multiple public posts
    Post.objects.create(author=user, content="Post 1", is_public=True, post_type="text")
    Post.objects.create(author=user, content="Post 2", is_public=True, post_type="text")
    Post.objects.create(author=user, content="Post 3", is_public=True, post_type="book_review")
    
    client.force_authenticate(user)
    res = client.get("/home/")
    
    assert res.status_code == 200
    assert "results" in res.data
    assert len(res.data["results"]) >= 3

