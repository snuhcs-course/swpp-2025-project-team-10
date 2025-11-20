"""
Tests for library books and wishlist endpoints.
"""

import uuid

from books.models import (
    Author,
    BookCopy,
    BookPublication,
    BookWishlist,
    Genre,
    Publisher,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class LibraryBooksEndpointTestCase(TestCase):
    """Test cases for /library/books/ endpoint."""

    def setUp(self):
        """Set up test client, user, and books."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="bookowner",
            email="bookowner@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Create test publisher and author
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = Author.objects.create(name="Test Author")

        # Helper to create a publication + copy for a given owner/title
        def make_copy(title, owner):
            publication = BookPublication.objects.create(
                title=title,
                publisher=self.publisher,
            )
            publication.authors.add(self.author)
            return BookCopy.objects.create(
                publication=publication, owner=owner
            )

        # Create books owned by user
        self.book1 = make_copy("My Book 1", self.user)
        self.book2 = make_copy("My Book 2", self.user)

        # Create book owned by other user
        self.other_book = make_copy("Other Book", self.other_user)

        self.url = "/library/books/"

    def test_get_my_books_success(self):
        """Test GET /library/books/ returns user's books."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verify response structure
        book_data = response.data[0]
        self.assertIn("id", book_data)
        self.assertIn("title", book_data)
        self.assertIn("author", book_data)
        self.assertIn("coverUrl", book_data)

    def test_get_my_books_only_returns_owned_books(self):
        """Test that only user's own books are returned."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book["title"] for book in response.data]

        self.assertIn("My Book 1", titles)
        self.assertIn("My Book 2", titles)
        self.assertNotIn("Other Book", titles)

    def test_get_my_books_empty_list(self):
        """Test GET returns empty list when user has no books."""
        # Create a new user with no books
        empty_user = User.objects.create_user(
            username="emptyuser",
            email="empty@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=empty_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_my_books_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LibraryWishlistEndpointTestCase(TestCase):
    """Test cases for /library/wishlist/ endpoint."""

    def setUp(self):
        """Set up test client, user, and wishlist."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="wishlistuser",
            email="wishlist@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Create test publisher and author
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = Author.objects.create(name="Test Author")

        def make_copy(title, owner):
            publication = BookPublication.objects.create(
                title=title,
                publisher=self.publisher,
            )
            publication.authors.add(self.author)
            return BookCopy.objects.create(
                publication=publication, owner=owner
            )

        # Create books
        self.book1 = make_copy("Wishlist Book 1", self.other_user)
        self.book2 = make_copy("Wishlist Book 2", self.other_user)

        # Add books to user's wishlist
        BookWishlist.objects.create(user=self.user, book=self.book1)
        BookWishlist.objects.create(user=self.user, book=self.book2)

        # Add book to other user's wishlist (should not appear in response)
        self.book3 = make_copy("Other Wishlist Book", self.other_user)
        BookWishlist.objects.create(user=self.other_user, book=self.book3)

        self.url = "/library/wishlist/"

    def test_get_my_wishlist_success(self):
        """Test GET /library/wishlist/ returns user's wishlist."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verify response structure
        book_data = response.data[0]
        self.assertIn("id", book_data)
        self.assertIn("title", book_data)
        self.assertIn("author", book_data)
        self.assertIn("coverUrl", book_data)

    def test_get_my_wishlist_only_returns_user_wishlist(self):
        """Test that only user's own wishlist is returned."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book["title"] for book in response.data]

        self.assertIn("Wishlist Book 1", titles)
        self.assertIn("Wishlist Book 2", titles)
        self.assertNotIn("Other Wishlist Book", titles)

    def test_get_my_wishlist_empty_list(self):
        """Test GET returns empty list when user has no wishlist items."""
        # Create user with empty wishlist
        new_user = User.objects.create_user(
            username="emptywishlist",
            email="empty@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=new_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_my_wishlist_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookWishlistToggleTestCase(TestCase):
    """Test cases for wishlist add/remove functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="wisher",
            email="wish@example.com",
            password="testpass123",
        )
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = Author.objects.create(name="Test Author")
        publication = BookPublication.objects.create(
            title="Wishlist Book",
            publisher=self.publisher,
        )
        publication.authors.add(self.author)
        self.book = BookCopy.objects.create(
            publication=publication,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_remove_from_wishlist_success(self):
        """Test removing a book from wishlist."""
        # Add to wishlist first
        BookWishlist.objects.create(user=self.user, book=self.book)

        url = f"/library/books/{self.book.id}/wishlist/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            BookWishlist.objects.filter(
                user=self.user, book=self.book
            ).exists()
        )

    def test_remove_from_wishlist_not_in_list(self):
        """Test removing a book that's not in wishlist."""
        url = f"/library/books/{self.book.id}/wishlist/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Not in wishlist", response.data["message"])

    def test_add_to_wishlist_duplicate(self):
        """Test adding book to wishlist when already in list."""
        # Add to wishlist first
        BookWishlist.objects.create(user=self.user, book=self.book)

        url = f"/library/books/{self.book.id}/wishlist/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not create duplicate
        self.assertEqual(
            BookWishlist.objects.filter(
                user=self.user, book=self.book
            ).count(),
            1,
        )
