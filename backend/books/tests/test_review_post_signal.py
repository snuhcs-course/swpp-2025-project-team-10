"""
Tests for BookReview to Post signal.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import BookReview, Book, Publisher, Author
from social.models import Post

User = get_user_model()


class BookReviewPostSignalTestCase(TestCase):
    """Test cases for automatic Post creation when BookReview is created."""

    def setUp(self):
        """Set up test user and book."""
        self.user = User.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="testpass123",
        )
        
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = Author.objects.create(name="Test Author")
        
        self.book = Book.objects.create(
            title="Test Book",
            owner=self.user,
            publisher=self.publisher,
        )
        self.book.authors.add(self.author)

    def test_post_created_when_review_created(self):
        """Test that Post is automatically created when BookReview is created."""
        initial_post_count = Post.objects.count()
        
        # Create a book review
        review = BookReview.objects.create(
            book=self.book,
            reviewer=self.user,
            book_title="Test Book",
            author_name="Test Author",
            content="Great book! Highly recommend.",
            rating=5,
        )
        
        # Verify Post was created
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        
        # Verify Post details
        post = Post.objects.latest("created_at")
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.post_type, "book_review")
        self.assertEqual(post.content, "Great book! Highly recommend.")
        self.assertEqual(post.related_book, self.book)
        self.assertTrue(post.is_public)

    def test_post_created_for_standalone_review(self):
        """Test that Post is created even for reviews without Book object."""
        initial_post_count = Post.objects.count()
        
        # Create a standalone review (no book FK)
        review = BookReview.objects.create(
            book=None,  # Standalone review
            reviewer=self.user,
            book_title="Standalone Book",
            author_name="Unknown Author",
            content="Review without book object.",
        )
        
        # Verify Post was created
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        
        # Verify Post details
        post = Post.objects.latest("created_at")
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.post_type, "book_review")
        self.assertEqual(post.content, "Review without book object.")
        self.assertIsNone(post.related_book)

    def test_post_not_created_on_review_update(self):
        """Test that Post is NOT created when updating existing review."""
        # Create initial review (this creates one Post)
        review = BookReview.objects.create(
            book=self.book,
            reviewer=self.user,
            book_title="Test Book",
            author_name="Test Author",
            content="Initial content",
        )
        
        initial_post_count = Post.objects.count()
        
        # Update the review
        review.content = "Updated content"
        review.save()
        
        # Verify no new Post was created
        self.assertEqual(Post.objects.count(), initial_post_count)

    def test_multiple_reviews_create_multiple_posts(self):
        """Test that multiple reviews create corresponding Posts."""
        initial_post_count = Post.objects.count()
        
        # Create multiple reviews
        for i in range(3):
            BookReview.objects.create(
                book=self.book,
                reviewer=self.user,
                book_title=f"Book {i}",
                author_name="Test Author",
                content=f"Review {i}",
            )
        
        # Verify 3 Posts were created
        self.assertEqual(Post.objects.count(), initial_post_count + 3)

    def test_post_id_is_integer(self):
        """Test that Post.id is an integer (not UUID)."""
        # Create a review
        review = BookReview.objects.create(
            book=self.book,
            reviewer=self.user,
            book_title="Test Book",
            author_name="Test Author",
            content="Test content",
        )
        
        # Get the created Post
        post = Post.objects.latest("created_at")
        
        # Verify id is an integer
        self.assertIsInstance(post.id, int)
