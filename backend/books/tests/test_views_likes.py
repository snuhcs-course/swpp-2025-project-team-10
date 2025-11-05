"""
Unit tests for review like/unlike views.
Tests POST /library/reviews/{id}/like/ endpoint.
"""

from books.models import BookReview, ReviewHelpfulVote
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ReviewLikeViewTestCase(APITestCase):
    """Test cases for liking reviews (POST /library/reviews/{id}/like/)."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )

        # Create a review
        self.review = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book!",
        )

    def test_like_review_unauthenticated(self):
        """Test that unauthenticated users cannot like reviews."""
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_review_authenticated(self):
        """Test that authenticated users can like reviews."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("review", response.data)
        self.assertEqual(response.data["review"]["likeCount"], 1)
        self.assertEqual(response.data["review"]["isLiked"], True)

        # Verify like was created in database
        self.assertTrue(
            ReviewHelpfulVote.objects.filter(
                review=self.review, user=self.user2
            ).exists()
        )

    def test_like_own_review(self):
        """Test that users can like their own reviews."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review"]["likeCount"], 1)

        # Verify like was created
        self.assertTrue(
            ReviewHelpfulVote.objects.filter(
                review=self.review, user=self.user1
            ).exists()
        )

    def test_like_nonexistent_review(self):
        """Test liking a review that doesn't exist."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("books:review-like", kwargs={"pk": 99999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)


class ReviewUnlikeViewTestCase(APITestCase):
    """Test cases for unliking reviews (POST /library/reviews/{id}/like/)."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )

        # Create a review
        self.review = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book!",
        )

    def test_unlike_review(self):
        """Test that users can unlike a previously liked review."""
        # First, create a like
        ReviewHelpfulVote.objects.create(review=self.review, user=self.user2)

        self.client.force_authenticate(user=self.user2)
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review"]["likeCount"], 0)
        self.assertEqual(response.data["review"]["isLiked"], False)

        # Verify like was removed from database
        self.assertFalse(
            ReviewHelpfulVote.objects.filter(
                review=self.review, user=self.user2
            ).exists()
        )

    def test_unlike_not_liked_review(self):
        """Test unliking a review that was never liked (should like it)."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})
        response = self.client.post(url)

        # Should create a like since it didn't exist
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review"]["likeCount"], 1)


class ReviewLikeToggleTestCase(APITestCase):
    """Test cases for toggling likes on reviews."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.review = BookReview.objects.create(
            reviewer=self.user,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book!",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("books:review-like", kwargs={"pk": self.review.pk})

    def test_like_toggle(self):
        """Test toggling like on and off multiple times."""
        # Like
        response = self.client.post(self.url)
        self.assertEqual(response.data["review"]["likeCount"], 1)

        # Unlike
        response = self.client.post(self.url)
        self.assertEqual(response.data["review"]["likeCount"], 0)

        # Like again
        response = self.client.post(self.url)
        self.assertEqual(response.data["review"]["likeCount"], 1)

        # Unlike again
        response = self.client.post(self.url)
        self.assertEqual(response.data["review"]["likeCount"], 0)


class ReviewMultipleLikesTestCase(APITestCase):
    """Test cases for multiple users liking the same review."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        self.user3 = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="testpass123",
        )

        self.review = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book!",
        )

    def test_multiple_users_like_same_review(self):
        """Test that multiple users can like the same review."""
        url = reverse("books:review-like", kwargs={"pk": self.review.pk})

        # User2 likes the review
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 1)

        # User3 likes the review
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 2)

        # User1 (owner) likes their own review
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 3)

        # Verify all likes exist
        self.assertEqual(
            ReviewHelpfulVote.objects.filter(review=self.review).count(), 3
        )

    def test_multiple_users_unlike_same_review(self):
        """Test that multiple users can unlike the same review."""
        # Create likes for all users
        ReviewHelpfulVote.objects.create(review=self.review, user=self.user1)
        ReviewHelpfulVote.objects.create(review=self.review, user=self.user2)
        ReviewHelpfulVote.objects.create(review=self.review, user=self.user3)

        url = reverse("books:review-like", kwargs={"pk": self.review.pk})

        # User2 unlikes
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 2)

        # User1 unlikes
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 1)

        # User3 unlikes
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(url)
        self.assertEqual(response.data["review"]["likeCount"], 0)

        # Verify no likes exist
        self.assertEqual(
            ReviewHelpfulVote.objects.filter(review=self.review).count(), 0
        )


class ReviewIsLikedFieldTestCase(APITestCase):
    """Test cases for isLiked field in review responses."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        self.review = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book!",
        )

    def test_is_liked_false_when_not_liked(self):
        """Test that isLiked is False when user hasn't liked the review."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("books:user-reviews")

        # Create a review by user2 to test
        review2 = BookReview.objects.create(
            reviewer=self.user2,
            book_title="Another Book",
            author_name="Another Author",
            content="Good book!",
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that isLiked is False for the review
        review_data = response.data["results"][0]
        self.assertEqual(review_data["isLiked"], False)

    def test_is_liked_true_when_liked(self):
        """Test that isLiked is True when user has liked the review."""
        # User2 creates a review
        review2 = BookReview.objects.create(
            reviewer=self.user2,
            book_title="Another Book",
            author_name="Another Author",
            content="Good book!",
        )

        # User2 likes their own review
        ReviewHelpfulVote.objects.create(review=review2, user=self.user2)

        self.client.force_authenticate(user=self.user2)
        url = reverse("books:user-reviews")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review_data = response.data["results"][0]
        self.assertEqual(review_data["isLiked"], True)

    def test_is_liked_after_like_toggle(self):
        """Test that isLiked updates correctly after toggling like."""
        self.client.force_authenticate(user=self.user1)
        like_url = reverse("books:review-like", kwargs={"pk": self.review.pk})

        # Like the review
        response = self.client.post(like_url)
        self.assertEqual(response.data["review"]["isLiked"], True)

        # Unlike the review
        response = self.client.post(like_url)
        self.assertEqual(response.data["review"]["isLiked"], False)

        # Like again
        response = self.client.post(like_url)
        self.assertEqual(response.data["review"]["isLiked"], True)
