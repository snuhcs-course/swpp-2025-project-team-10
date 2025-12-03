import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from books.models import (
    BookCopy, 
    BookPublication, 
    Publisher, 
    Author as BookAuthor,
    BookWishlist
)

from notify.models import Notification

from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestWishlistToggle:
    """Test suite for wishlist toggle functionality"""

    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        
        # Create two users: one who owns books, one who wishlists them
        self.book_owner = User.objects.create(
            username="owner", 
            email="owner@example.com", 
            first_name="Owner", 
            last_name="User"
        )
        
        self.wisher = User.objects.create(
            username="wisher", 
            email="wisher@example.com", 
            first_name="Wisher", 
            last_name="User"
        )

        self.user = User.objects.create_user(
            username="wisher_user",
            email="wisher_user@example.com",
            password="testpass123"
        )

        
        # Create book data
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = BookAuthor.objects.create(name="Test Author")
        self.publication = BookPublication.objects.create(
            title="Test Book",
            publisher=self.publisher
        )
        self.publication.authors.add(self.author)
        
        # Create a book owned by book_owner
        self.book = BookCopy.objects.create(
            publication=self.publication,
            owner=self.book_owner  # NOT the wisher!
        )

    def test_toggle_wishlist_creates_and_removes(self):
        """Test adding and removing a book from wishlist"""
        # Authenticate as the wisher (NOT the book owner)
        self.client.force_authenticate(self.wisher)
        
        url = reverse("books:toggle-wishlist", kwargs={"book_id": self.book.id})
        
        # --- ADD TO WISHLIST (POST) ---
        res = self.client.post(url)
        
        assert res.status_code == 201  # Created
        assert res.data["wishlisted"] is True
        assert res.data["created"] is True
        
        # Verify wishlist item was created
        assert BookWishlist.objects.filter(user=self.wisher, book=self.book).exists()
        
        # Verify notification was sent to book owner
        notification = Notification.objects.filter(
            recipient=self.book_owner,
            sender=self.wisher,
            notification_type="book_wishlisted"
        ).first()
        assert notification is not None
        assert self.book.title in notification.message
        
        # --- ADD AGAIN (IDEMPOTENT - should return 200, not create new) ---
        res = self.client.post(url)
        
        assert res.status_code == 200  # OK (already exists)
        assert res.data["wishlisted"] is True
        assert res.data["created"] is False
        
        # Still only one wishlist item
        assert BookWishlist.objects.filter(user=self.wisher, book=self.book).count() == 1
        
        # Still only one notification (no duplicate)
        assert Notification.objects.filter(
            recipient=self.book_owner,
            sender=self.wisher,
            notification_type="book_wishlisted"
        ).count() == 1
        
        # --- REMOVE FROM WISHLIST (DELETE) ---
        res = self.client.delete(url)
        
        assert res.status_code == 200
        assert res.data["wishlisted"] is False
        assert res.data["removed"] is True
        
        # Verify wishlist item was deleted
        assert not BookWishlist.objects.filter(user=self.wisher, book=self.book).exists()
        
        # --- REMOVE AGAIN (should still return 200, not error) ---
        res = self.client.delete(url)
        
        assert res.status_code == 200
        assert res.data["wishlisted"] is False
        assert res.data["removed"] is False
        assert "Not in wishlist" in res.data["message"]

    def test_cannot_wishlist_own_book(self):
        """Test that users cannot wishlist their own books"""
        # Authenticate as the book owner
        self.client.force_authenticate(self.book_owner)
        
        url = reverse("books:toggle-wishlist", kwargs={"book_id": self.book.id})
        
        # Try to wishlist own book
        res = self.client.post(url)
        
        assert res.status_code == 400
        assert "error" in res.data
        assert "own book" in res.data["error"].lower()
        
        # Verify no wishlist item was created
        assert not BookWishlist.objects.filter(user=self.book_owner, book=self.book).exists()
        
        # Verify no notification was sent
        assert not Notification.objects.filter(
            notification_type="book_wishlisted"
        ).exists()

    def test_wishlist_nonexistent_book(self):
        """Test wishlisting a book that doesn't exist"""
        self.client.force_authenticate(self.wisher)
        
        # Use a UUID that doesn't exist
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse("books:toggle-wishlist", kwargs={"book_id": fake_uuid})
        
        res = self.client.post(url)
        
        assert res.status_code == 404

    def test_unauthenticated_user_cannot_wishlist(self):
        """Test that unauthenticated users cannot access wishlist"""
        # Don't authenticate
        url = reverse("books:toggle-wishlist", kwargs={"book_id": self.book.id})
        
        res = self.client.post(url)
        assert res.status_code == 401
        
        res = self.client.delete(url)
        assert res.status_code == 401

    def test_multiple_users_can_wishlist_same_book(self):
        """Test that multiple users can wishlist the same book"""
        # Create another wisher
        another_wisher = User.objects.create(
            username="another", 
            email="another@example.com"
        )
        
        url = reverse("books:toggle-wishlist", kwargs={"book_id": self.book.id})
        
        # First wisher adds to wishlist
        self.client.force_authenticate(self.wisher)
        res1 = self.client.post(url)
        assert res1.status_code == 201
        
        # Second wisher adds to wishlist
        self.client.force_authenticate(another_wisher)
        res2 = self.client.post(url)
        assert res2.status_code == 201
        
        # Both wishlist items exist
        assert BookWishlist.objects.filter(book=self.book).count() == 2
        assert BookWishlist.objects.filter(user=self.wisher, book=self.book).exists()
        assert BookWishlist.objects.filter(user=another_wisher, book=self.book).exists()
        
        # Both users got notifications sent to book owner
        assert Notification.objects.filter(
            recipient=self.book_owner,
            notification_type="book_wishlisted"
        ).count() == 2

    def test_wishlist_with_priority_and_notes(self):
        """Test wishlist with custom priority and notes"""
        self.client.force_authenticate(self.wisher)
        
        url = reverse("books:toggle-wishlist", kwargs={"book_id": self.book.id})
        
        # Add to wishlist
        res = self.client.post(url)
        assert res.status_code == 201
        
        # Update the wishlist item with priority and notes
        wishlist_item = BookWishlist.objects.get(user=self.wisher, book=self.book)
        wishlist_item.priority = 5
        wishlist_item.notes = "Really want to read this!"
        wishlist_item.save()
        
        # Verify
        wishlist_item.refresh_from_db()
        assert wishlist_item.priority == 5
        assert wishlist_item.notes == "Really want to read this!"

    def test_wishlist_ordering(self):
        """Test that wishlist items are ordered by priority then created_at"""
        self.client.force_authenticate(self.wisher)
        
        # Create multiple books
        book1 = BookCopy.objects.create(
            publication=self.publication,
            owner=self.book_owner
        )
        book2 = BookCopy.objects.create(
            publication=self.publication,
            owner=self.book_owner
        )
        
        # Add to wishlist with different priorities
        wishlist1 = BookWishlist.objects.create(
            user=self.wisher,
            book=book1,
            priority=3
        )
        wishlist2 = BookWishlist.objects.create(
            user=self.wisher,
            book=book2,
            priority=5
        )
        
        # Get ordered wishlist
        wishlist_items = BookWishlist.objects.filter(user=self.wisher)
        
        # Higher priority (5) should come first
        assert wishlist_items[0].id == wishlist2.id
        assert wishlist_items[1].id == wishlist1.id