"""
Unit tests for review list and create views.
Tests GET /library/reviews/ and POST /library/reviews/ endpoints.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import BookReview

User = get_user_model()


class ReviewListViewTestCase(APITestCase):
    """Test cases for listing user reviews (GET /library/reviews/)."""

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

        # Create some reviews for user1
        self.review1 = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book 1",
            author_name="Test Author 1",
            content="Great book!",
            image_urls=["https://example.com/image1.jpg"],
        )
        self.review2 = BookReview.objects.create(
            reviewer=self.user1,
            book_title="Test Book 2",
            author_name="Test Author 2",
            content="Amazing read!",
            image_urls=[],
        )

        # Create a review for user2
        self.review3 = BookReview.objects.create(
            reviewer=self.user2,
            book_title="Test Book 3",
            author_name="Test Author 3",
            content="Interesting story!",
        )

        self.list_url = reverse("books:user-reviews")

    def test_list_reviews_unauthenticated(self):
        """Test that unauthenticated users cannot list reviews."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_authenticated(self):
        """Test that authenticated users can list their own reviews."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

        # Check response format
        review_data = response.data["results"][0]
        self.assertIn("id", review_data)
        self.assertIn("bookTitle", review_data)
        self.assertIn("authorName", review_data)
        self.assertIn("userName", review_data)
        self.assertIn("userProfile", review_data)
        self.assertIn("content", review_data)
        self.assertIn("imageUrls", review_data)
        self.assertIn("likeCount", review_data)
        self.assertIn("createdAt", review_data)
        self.assertIn("isLiked", review_data)

    def test_list_reviews_only_own_reviews(self):
        """Test that users only see their own reviews."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["bookTitle"], "Test Book 3"
        )

    def test_list_reviews_empty(self):
        """Test listing reviews when user has no reviews."""
        user3 = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=user3)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 0)


class ReviewCreateViewTestCase(APITestCase):
    """Test cases for creating reviews (POST /library/reviews/)."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.list_url = reverse("books:user-reviews")

    def test_create_review_unauthenticated(self):
        """Test that unauthenticated users cannot create reviews."""
        data = {
            "bookTitle": "New Book",
            "authorName": "New Author",
            "content": "Great book!",
            "imageUrls": [],
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated(self):
        """Test that authenticated users can create reviews."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "New Book",
            "authorName": "New Author",
            "content": "Great book!",
            "imageUrls": ["https://example.com/new.jpg"],
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["bookTitle"], "New Book")
        self.assertEqual(response.data["authorName"], "New Author")
        self.assertEqual(response.data["content"], "Great book!")
        self.assertEqual(response.data["userName"], "testuser")
        self.assertEqual(
            response.data["imageUrls"], ["https://example.com/new.jpg"]
        )

        # Verify review was created in database
        self.assertEqual(
            BookReview.objects.filter(reviewer=self.user).count(), 1
        )

    def test_create_review_without_images(self):
        """Test creating a review without images."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "Book Without Images",
            "authorName": "Author Name",
            "content": "Good book!",
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["imageUrls"], [])

    def test_create_review_without_author(self):
        """Test creating a review without author name."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "Book Without Author",
            "authorName": "",
            "content": "Good book!",
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["authorName"], "")

    def test_create_review_invalid_empty_title(self):
        """Test creating a review with empty title."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "",  # Empty title
            "authorName": "Author",
            "content": "Content",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_missing_title(self):
        """Test creating a review without title."""
        self.client.force_authenticate(user=self.user)
        data = {
            "authorName": "Author",
            "content": "Content",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_missing_content(self):
        """Test creating a review without content."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "Book Title",
            "authorName": "Author",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_with_multiple_images(self):
        """Test creating a review with multiple images."""
        self.client.force_authenticate(user=self.user)
        data = {
            "bookTitle": "Book With Multiple Images",
            "authorName": "Author Name",
            "content": "Great book with pictures!",
            "imageUrls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
                "https://example.com/image3.jpg",
            ],
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["imageUrls"]), 3)
