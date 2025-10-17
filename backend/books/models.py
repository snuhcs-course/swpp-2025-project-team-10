import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from PIL import Image
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


class Book(models.Model):
    """
    Model to represent books in the system.
    """

    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("very_good", "Very Good"),
        ("good", "Good"),
        ("acceptable", "Acceptable"),
        ("poor", "Poor"),
    ]

    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("pending", "Pending Trade"),
        ("traded", "Traded"),
        ("not_available", "Not Available"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Publication Details
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

    # Content
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)
    tags = TaggableManager(blank=True)

    # Images
    cover_image = models.ImageField(
        upload_to="book_covers/", null=True, blank=True
    )

    # Owner Information
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="books"
    )
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good"
    )
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="available"
    )

    # Owner's Notes
    owner_notes = models.TextField(
        blank=True,
        help_text="Additional notes about the book's condition or special features",
    )

    # Barter Information
    is_for_barter = models.BooleanField(default=True)
    preferred_genres_for_trade = models.ManyToManyField(
        Genre,
        related_name="books_wanted_for_trade",
        blank=True,
        help_text="Genres you'd like to receive in exchange",
    )

    # Ratings and Reviews
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book"
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn_13"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["availability"]),
            models.Index(fields=["is_for_barter"]),
        ]

    def __str__(self):
        return f"{self.title} by {', '.join([author.name for author in self.authors.all()])}"

    def save(self, *args, **kwargs):
        """Override save to resize cover image."""
        super().save(*args, **kwargs)

        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 600 or img.width > 400:
                output_size = (400, 600)
                img.thumbnail(output_size)
                img.save(self.cover_image.path)

    @property
    def author_names(self):
        """Return comma-separated author names."""
        return ", ".join([author.name for author in self.authors.all()])

    @property
    def is_available_for_barter(self):
        """Check if book is available for bartering."""
        return self.is_for_barter and self.availability == "available"


class BookReview(models.Model):
    """
    Model to represent book reviews by users.
    """

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="book_reviews"
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate the book from 1 to 5 stars",
    )
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    # Helpful votes
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
        unique_together = ("book", "reviewer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review of {self.book.title} by {self.reviewer.username}"

    @property
    def helpful_count(self):
        """Return the number of helpful votes."""
        return self.helpful_votes.count()


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
        Book, on_delete=models.CASCADE, related_name="wishlisted_by"
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
        Book, related_name="collections", blank=True
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
        Book, on_delete=models.CASCADE, related_name="reading_statuses"
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

    @property
    def reading_progress(self):
        """Calculate reading progress percentage."""
        if self.book.pages and self.pages_read:
            return min(100, (self.pages_read / self.book.pages) * 100)
        return 0
