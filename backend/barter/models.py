import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class BarterRequest(models.Model):
    """
    Model to represent barter requests between users.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("disputed", "Disputed"),
    ]

    MEETING_TYPE_CHOICES = [
        ("in_person", "In Person"),
        ("mail", "Mail Exchange"),
        ("pickup", "Pickup/Dropoff"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_barter_requests"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_barter_requests"
    )

    # Books Involved
    offered_books = models.ManyToManyField(
        "books.Book",
        related_name="offered_in_barters",
        help_text="Books offered by the requester",
    )
    requested_books = models.ManyToManyField(
        "books.Book",
        related_name="requested_in_barters",
        help_text="Books requested from the recipient",
    )

    # Request Details
    message = models.TextField(
        help_text="Message from requester explaining the barter request"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    # Meeting Details
    preferred_meeting_type = models.CharField(
        max_length=20, choices=MEETING_TYPE_CHOICES, default="in_person"
    )
    proposed_meeting_location = models.CharField(max_length=200, blank=True)
    proposed_meeting_time = models.DateTimeField(null=True, blank=True)

    # Response from recipient
    response_message = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)

    # Completion Details
    completed_date = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When this barter request expires"
    )

    class Meta:
        db_table = "barter_barter_request"
        verbose_name = "Barter Request"
        verbose_name_plural = "Barter Requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requester"]),
            models.Index(fields=["recipient"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Barter Request from {self.requester.username} to {self.recipient.username}"

    @property
    def is_active(self):
        """Check if the barter request is still active."""
        return self.status in ["pending", "accepted"]

    @property
    def offered_books_count(self):
        """Return the number of books offered."""
        return self.offered_books.count()

    @property
    def requested_books_count(self):
        """Return the number of books requested."""
        return self.requested_books.count()


class BarterCounter(models.Model):
    """
    Model to represent counter-offers in barter negotiations.
    """

    original_request = models.ForeignKey(
        BarterRequest, on_delete=models.CASCADE, related_name="counter_offers"
    )
    counter_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Counter Offer Details
    offered_books = models.ManyToManyField(
        "books.Book", related_name="counter_offered_books", blank=True
    )
    requested_books = models.ManyToManyField(
        "books.Book", related_name="counter_requested_books", blank=True
    )

    message = models.TextField(help_text="Explanation of the counter offer")

    # Meeting Details (can be different from original)
    preferred_meeting_type = models.CharField(
        max_length=20, choices=BarterRequest.MEETING_TYPE_CHOICES, blank=True
    )
    proposed_meeting_location = models.CharField(max_length=200, blank=True)
    proposed_meeting_time = models.DateTimeField(null=True, blank=True)

    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "barter_barter_counter"
        verbose_name = "Barter Counter Offer"
        verbose_name_plural = "Barter Counter Offers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Counter offer by {self.counter_by.username} for request {self.original_request.id}"


class BarterTransaction(models.Model):
    """
    Model to track completed barter transactions.
    """

    TRANSACTION_STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("disputed", "Disputed"),
    ]

    barter_request = models.OneToOneField(
        BarterRequest, on_delete=models.CASCADE, related_name="transaction"
    )

    # Transaction Details
    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS_CHOICES,
        default="in_progress",
    )

    # Actual Meeting Details
    actual_meeting_location = models.CharField(max_length=200, blank=True)
    actual_meeting_time = models.DateTimeField(null=True, blank=True)
    meeting_type = models.CharField(
        max_length=20, choices=BarterRequest.MEETING_TYPE_CHOICES
    )

    # Completion
    completed_date = models.DateTimeField(null=True, blank=True)
    completion_confirmed_by_requester = models.BooleanField(default=False)
    completion_confirmed_by_recipient = models.BooleanField(default=False)

    # Notes
    transaction_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "barter_barter_transaction"
        verbose_name = "Barter Transaction"
        verbose_name_plural = "Barter Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction for {self.barter_request}"

    @property
    def is_completed(self):
        """Check if transaction is completed by both parties."""
        return (
            self.completion_confirmed_by_requester
            and self.completion_confirmed_by_recipient
        )


class BarterRating(models.Model):
    """
    Model to store ratings and feedback after completed barters.
    """

    transaction = models.ForeignKey(
        BarterTransaction, on_delete=models.CASCADE, related_name="ratings"
    )
    rater = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_ratings"
    )
    rated_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_ratings"
    )

    # Rating Details
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate the other user from 1 to 5 stars",
    )

    # Specific Ratings
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How well did they communicate?",
    )
    punctuality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Were they on time for the meeting?",
    )
    book_condition_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Was the book condition as described?",
    )

    # Feedback
    feedback = models.TextField(
        blank=True, help_text="Optional feedback about the barter experience"
    )

    # Flags
    would_barter_again = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "barter_barter_rating"
        verbose_name = "Barter Rating"
        verbose_name_plural = "Barter Ratings"
        unique_together = ("transaction", "rater", "rated_user")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Rating by {self.rater.username} for {self.rated_user.username}"
        )
