from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from social.models import Post, PostLike
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class PostViewTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
        self.other_user = User.objects.create_user(username="user2", email="user2@example.com", password="password123")

        # Generate and set JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # URLs
        self.create_url = "/posts/create/"
        self.home_feed_url = "/home/"

        # Create sample posts
        self.public_post = Post.objects.create(author=self.other_user, content="Public post", is_public=True)
        self.private_post = Post.objects.create(author=self.other_user, content="Private post", is_public=False)

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
        self.assertTrue(PostLike.objects.filter(post=self.public_post, user=self.user).exists())

        # Unlike the post (toggle)
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PostLike.objects.filter(post=self.public_post, user=self.user).exists())

    def test_like_post_not_found(self):
        """Return 404 if post does not exist."""
        like_url = "/posts/9999/like/"
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
