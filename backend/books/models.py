import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from social.models import Post
from taggit.managers import TaggableManager

User = get_user_model()


class Genre(models.Model):
    """
    Model to represent book genres.
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_genre"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Model to represent book authors.
    """

    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_author"
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """
    Model to represent book publishers.
    """

    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_publisher"
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Translator(models.Model):
    """
    Model to represent book translators.
    """

    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_translator"
        verbose_name = "Translator"
        verbose_name_plural = "Translators"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookPublication(models.Model):
    """Metadata shared across all user-owned copies."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    authors = models.ManyToManyField(Author, related_name="publications")
    translators = models.ManyToManyField(
        Translator, related_name="publications", blank=True
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )

    isbn_10 = models.CharField(
        max_length=10, blank=True, unique=True, null=True
    )
    isbn_13 = models.CharField(
        max_length=13, blank=True, unique=True, null=True
    )
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    pages = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    language = models.CharField(max_length=30, default="English")
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(
        Genre, related_name="publications", blank=True
    )

    cover_image = models.ImageField(
        upload_to="book_covers/", null=True, blank=True
    )

    external_url = models.URLField(
        max_length=1024,
        blank=True,
        help_text="URL to the book detail page on external API (e.g., Kakao)",
    )
    original_price = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Original price from external API",
    )
    sale_price = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Sale price from external API",
    )
    sales_status = models.CharField(
        max_length=50,
        blank=True,
        help_text="Sales status from external API (e.g., 정상, 품절, 절판)",
    )
    category_scores = models.JSONField(
        default=list,
        blank=True,
        help_text="Cached LLM category scores (label + score dicts)",
    )
    taste_profile = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cached LLM taste profile (genres, moods, purposes, length)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book_publication"
        verbose_name = "Book Publication"
        verbose_name_plural = "Book Publications"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn_13"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Resize cover image for consistent storage."""
        super().save(*args, **kwargs)

        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 600 or img.width > 400:
                output_size = (400, 600)
                img.thumbnail(output_size)
                img.save(self.cover_image.path)

    @property
    def author_names(self):
        return ", ".join(author.name for author in self.authors.all())


class BookCopy(models.Model):
    """A user-owned copy of a publication with personal metadata."""

    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("very_good", "Very Good"),
        ("good", "Good"),
        ("acceptable", "Acceptable"),
        ("poor", "Poor"),
    ]

    TRADE_STATUS_CHOICES = [
        ("available", "Available for Trade"),
        ("pending", "Pending Trade"),
        ("traded", "Traded"),
        ("not_available", "Not Available"),
    ]
    AVAILABILITY_CHOICES = TRADE_STATUS_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(
        BookPublication,
        on_delete=models.CASCADE,
        related_name="copies",
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="book_copies"
    )
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good"
    )
    tags = TaggableManager(blank=True)
    # Owner's Notes
    owner_notes = models.TextField(
        blank=True,
        help_text="Additional notes about the book's condition or special features",
    )
    # Barter Status (System-managed, changes during trade lifecycle)
    # This field tracks the current trade state of the book:
    # - "available": Book is ready for barter (no pending trades)
    # - "not_available": Book is locked in a pending barter request
    # - "traded": Book has been successfully traded to another user
    # - "pending": (deprecated, use "not_available" instead)
    # System automatically sets this to "not_available" when a barter request is created,
    # and restores to "available" when trade is rejected/cancelled or completed.
    trade_status = models.CharField(
        max_length=20,
        choices=TRADE_STATUS_CHOICES,
        default="available",
        db_column="availability",  # reuse legacy column created before BookCopy rename
    )

    # Barter Preference (User-controlled, owner's trading preference)
    # This field represents the owner's decision about whether they want to trade this book:
    # - True: Owner is willing to trade this book (book will appear in barter searches)
    # - False: Owner wants to keep this book (book won't be available for barter requests)
    # User can toggle this in their library settings to control which books are tradeable.
    # Even if availability="available", barter requests will be rejected if is_for_barter=False.
    is_for_barter = models.BooleanField(
        default=True,
        help_text="Whether the owner wants to trade this book (user setting)",
    )
    preferred_genres_for_trade = models.ManyToManyField(
        Genre,
        related_name="book_copies_wanted_for_trade",
        blank=True,
        help_text="Genres you'd like to receive in exchange",
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book_copy"
        verbose_name = "Book Copy"
        verbose_name_plural = "Book Copies"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["trade_status"]),
            models.Index(fields=["is_for_barter"]),
        ]

    _PUBLICATION_FIELD_PROXY = {
        "subtitle",
        "isbn_10",
        "isbn_13",
        "publication_date",
        "edition",
        "pages",
        "language",
        "description",
        "external_url",
        "original_price",
        "sale_price",
        "sales_status",
        "cover_image",
        "publisher",
        "authors",
        "translators",
        "genres",
    }

    def __str__(self):
        return f"{self.owner.username}'s copy of {self.publication.title}"

    @property
    def title(self):
        return self.publication.title

    @property
    def subtitle(self):
        return self.publication.subtitle

    @property
    def isbn_10(self):
        return self.publication.isbn_10

    @property
    def isbn_13(self):
        return self.publication.isbn_13

    @property
    def author_names(self):
        return self.publication.author_names

    @property
    def is_available_for_barter(self):
        """Check if book is available for bartering."""
        return self.is_for_barter and self.trade_status == "available"

    @property
    def availability(self):
        """Backward-compatible alias for legacy column name."""
        return self.trade_status

    def __getattr__(self, item):
        if item in self._PUBLICATION_FIELD_PROXY:
            return getattr(self.publication, item)
        return super().__getattr__(item)


class BookReview(models.Model):
    """
    Model to represent book reviews by users.
    Supports both book-linked reviews and standalone reviews.
    """

    # Book reference (optional for standalone reviews)
    book = models.ForeignKey(
        BookCopy,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="book_reviews"
    )

    # Book information (for standalone reviews without Book object)
    book_title = models.CharField(
        max_length=200, help_text="Title of the book being reviewed"
    )
    author_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Author(s) of the book being reviewed",
    )

    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate the book from 1 to 5 stars",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    # Images (stored as JSON array of URLs)
    image_urls = models.JSONField(
        default=list, blank=True, help_text="List of image URLs for the review"
    )

    # Likes (using helpful_votes as likes for compatibility)
    helpful_votes = models.ManyToManyField(
        User,
        through="ReviewHelpfulVote",
        related_name="helpful_reviews",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book_review"
        verbose_name = "Book Review"
        verbose_name_plural = "Book Reviews"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reviewer", "-created_at"]),
            models.Index(fields=["book_title"]),
        ]

    def __str__(self):
        if self.book:
            return f"Review of {self.book.title} by {self.reviewer.username}"
        return f"Review of {self.book_title} by {self.reviewer.username}"

    @property
    def helpful_count(self):
        """Return the number of helpful votes (likes)."""
        return self.helpful_votes.count()

    @property
    def like_count(self):
        """Alias for helpful_count to match frontend expectations."""
        return self.helpful_count


class ReviewHelpfulVote(models.Model):
    """
    Model to track helpful votes on reviews.
    """

    review = models.ForeignKey(BookReview, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_review_helpful_vote"
        unique_together = ("review", "user")
        verbose_name = "Review Helpful Vote"
        verbose_name_plural = "Review Helpful Votes"

    def __str__(self):
        return f"{self.user.username} found review helpful"


class BookWishlist(models.Model):
    """
    Model to represent user's book wishlist.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist"
    )
    book = models.ForeignKey(
        BookCopy, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Priority level (1=Low, 5=High)",
    )
    notes = models.TextField(
        blank=True, help_text="Personal notes about why you want this book"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_book_wishlist"
        verbose_name = "Book Wishlist Item"
        verbose_name_plural = "Book Wishlist Items"
        unique_together = ("user", "book")
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"{self.user.username} wants {self.book.title}"


class BookCollection(models.Model):
    """
    Model to represent user-created book collections.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collections"
    )
    books = models.ManyToManyField(
        BookCopy, related_name="collections", blank=True
    )

    is_public = models.BooleanField(
        default=True, help_text="Make this collection visible to others"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book_collection"
        verbose_name = "Book Collection"
        verbose_name_plural = "Book Collections"
        unique_together = ("owner", "name")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} by {self.owner.username}"

    @property
    def book_count(self):
        """Return the number of books in this collection."""
        return self.books.count()


class ReadingStatus(models.Model):
    """
    Model to track user's reading status for books.
    """

    STATUS_CHOICES = [
        ("want_to_read", "Want to Read"),
        ("currently_reading", "Currently Reading"),
        ("read", "Read"),
        ("did_not_finish", "Did Not Finish"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reading_statuses"
    )
    book = models.ForeignKey(
        BookCopy, on_delete=models.CASCADE, related_name="reading_statuses"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="want_to_read"
    )

    # Reading Progress
    pages_read = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)

    # Personal Rating (different from public review)
    personal_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    notes = models.TextField(blank=True, help_text="Personal reading notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_reading_status"
        verbose_name = "Reading Status"
        verbose_name_plural = "Reading Statuses"
        unique_together = ("user", "book")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.get_status_display()})"

    def get_status_display(self):
        """Return a human-readable status label even if Django's helper is unavailable."""
        choices = dict(self.STATUS_CHOICES)
        return choices.get(self.status, self.status)

    @property
    def reading_progress(self):
        """Calculate reading progress percentage."""
        if self.book.pages and self.pages_read:
            return min(100, (self.pages_read / self.book.pages) * 100)
        return 0


# --- Signal: Create Post when BookReview is created ---
@receiver(post_save, sender=BookReview)
def create_post_for_review(sender, instance, created, **kwargs):
    if created:
        Post.objects.create(
            author=instance.reviewer,
            post_type="book_review",
            content=instance.content,
            related_book=instance.book,
            is_public=True,
        )
