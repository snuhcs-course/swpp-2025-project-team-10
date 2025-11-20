"""
Tests for Post model and serializer with integer ID.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from social.models import Post, PostLike
from social.serializers import PostSerializer

User = get_user_model()


class PostIntegerIdTestCase(TestCase):
    """Test cases for Post model with integer ID."""

    def setUp(self):
        """Set up test user and post."""
        self.user = User.objects.create_user(
            username="postuser",
            email="post@example.com",
            password="testpass123",
        )

    def test_post_id_is_autofield(self):
        """Test that Post.id is an AutoField (integer)."""
        post = Post.objects.create(
            author=self.user,
            post_type="text",
            content="Test post",
            is_public=True,
        )

        # Verify id is an integer
        self.assertIsInstance(post.id, int)

    def test_post_ids_are_sequential(self):
        """Test that Post IDs are sequential integers."""
        post1 = Post.objects.create(
            author=self.user,
            post_type="text",
            content="Post 1",
            is_public=True,
        )
        post2 = Post.objects.create(
            author=self.user,
            post_type="text",
            content="Post 2",
            is_public=True,
        )

        # IDs should be sequential
        self.assertEqual(post2.id, post1.id + 1)

    def test_post_serializer_returns_integer_id(self):
        """Test that PostSerializer returns integer ID."""
        post = Post.objects.create(
            author=self.user,
            post_type="text",
            content="Test post",
            is_public=True,
        )

        serializer = PostSerializer(post)

        # Verify id is integer in serialized data
        self.assertIsInstance(serializer.data["id"], int)


class HomeFeedEndpointTestCase(TestCase):
    """Test cases for home feed endpoint."""

    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="feeduser",
            email="feed@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Create posts
        self.post1 = Post.objects.create(
            author=self.user,
            post_type="text",
            content="My post",
            is_public=True,
        )
        self.post2 = Post.objects.create(
            author=self.other_user,
            post_type="text",
            content="Other's post",
            is_public=True,
        )
        self.private_post = Post.objects.create(
            author=self.other_user,
            post_type="text",
            content="Private post",
            is_public=False,
        )

        self.url = "/home/"

    def test_home_feed_returns_public_posts(self):
        """Test GET /home/ returns all public posts."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        # Should have 2 public posts
        self.assertEqual(len(response.data["results"]), 2)

    def test_home_feed_excludes_private_posts(self):
        """Test that private posts are not included in feed."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post_ids = [post["id"] for post in response.data["results"]]
        self.assertIn(self.post1.id, post_ids)
        self.assertIn(self.post2.id, post_ids)
        self.assertNotIn(self.private_post.id, post_ids)

    def test_home_feed_ordered_by_created_at_desc(self):
        """Test that posts are ordered by creation date (newest first)."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Most recent post should be first
        first_post_id = response.data["results"][0]["id"]
        self.assertEqual(first_post_id, self.post2.id)

    def test_post_like_toggle(self):
        """Test POST /posts/{id}/like/ toggles like."""
        url = f"/posts/{self.post2.id}/like/"

        # Like the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify like was added
        self.assertTrue(
            PostLike.objects.filter(post=self.post2, user=self.user).exists()
        )

        # Unlike the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify like was removed
        self.assertFalse(
            PostLike.objects.filter(post=self.post2, user=self.user).exists()
        )

    def test_home_feed_includes_integer_post_ids(self):
        """Test that home feed returns integer post IDs."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for post_data in response.data["results"]:
            self.assertIsInstance(post_data["id"], int)

    def test_home_feed_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
