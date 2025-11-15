"""
Tests for library books and wishlist endpoints.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book, BookWishlist, Genre, Author, Publisher
import uuid

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
        
        # Create books owned by user
        self.book1 = Book.objects.create(
            title="My Book 1",
            owner=self.user,
            publisher=self.publisher,
        )
        self.book1.authors.add(self.author)
        
        self.book2 = Book.objects.create(
            title="My Book 2",
            owner=self.user,
            publisher=self.publisher,
        )
        self.book2.authors.add(self.author)
        
        # Create book owned by other user
        self.other_book = Book.objects.create(
            title="Other Book",
            owner=self.other_user,
            publisher=self.publisher,
        )
        self.other_book.authors.add(self.author)
        
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
        
        # Create books
        self.book1 = Book.objects.create(
            title="Wishlist Book 1",
            owner=self.other_user,
            publisher=self.publisher,
        )
        self.book1.authors.add(self.author)
        
        self.book2 = Book.objects.create(
            title="Wishlist Book 2",
            owner=self.other_user,
            publisher=self.publisher,
        )
        self.book2.authors.add(self.author)
        
        # Add books to user's wishlist
        BookWishlist.objects.create(user=self.user, book=self.book1)
        BookWishlist.objects.create(user=self.user, book=self.book2)
        
        # Add book to other user's wishlist (should not appear in response)
        self.book3 = Book.objects.create(
            title="Other Wishlist Book",
            owner=self.other_user,
            publisher=self.publisher,
        )
        self.book3.authors.add(self.author)
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
        self.book = Book.objects.create(
            title="Wishlist Book",
            owner=self.user,
            publisher=self.publisher,
        )
        self.book.authors.add(self.author)
        self.client.force_authenticate(user=self.user)

    def test_remove_from_wishlist_success(self):
        """Test removing a book from wishlist."""
        # Add to wishlist first
        BookWishlist.objects.create(user=self.user, book=self.book)
        
        url = f"/library/books/{self.book.id}/wishlist/"
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(BookWishlist.objects.filter(user=self.user, book=self.book).exists())

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
        self.assertEqual(BookWishlist.objects.filter(user=self.user, book=self.book).count(), 1)
