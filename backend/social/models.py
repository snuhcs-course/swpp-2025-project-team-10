import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    """
    Model to represent social posts by users.
    """

    POST_TYPE_CHOICES = [
        ("text", "Text Post"),
        ("book_review", "Book Review"),
        ("book_recommendation", "Book Recommendation"),
        ("reading_update", "Reading Update"),
        ("barter_success", "Successful Barter"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    post_type = models.CharField(
        max_length=20, choices=POST_TYPE_CHOICES, default="text"
    )

    # Content
    content = models.TextField(help_text="Share your thoughts about books!")

    # Related Objects
    related_book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_posts",
        help_text="Book this post is about (optional)",
    )

    # Images
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)

    # Engagement
    likes = models.ManyToManyField(
        User, through="PostLike", related_name="liked_posts", blank=True
    )

    # Visibility
    is_public = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["post_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return (
            f"Post by {self.author.username} - {self.get_post_type_display()}"
        )

    @property
    def like_count(self):
        """Return the number of likes."""
        return self.likes.count()

    @property
    def comment_count(self):
        """Return the number of comments."""
        return self.comments.count()


class PostLike(models.Model):
    """
    Model to track likes on posts.
    """

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_post_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_post_like"
        unique_together = ("post", "user")
        verbose_name = "Post Like"
        verbose_name_plural = "Post Likes"

    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class Comment(models.Model):
    """
    Model to represent comments on posts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    content = models.TextField(max_length=500)

    # Reply functionality
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    # Engagement
    likes = models.ManyToManyField(
        User, through="CommentLike", related_name="liked_comments", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_comment"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["author"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"

    @property
    def like_count(self):
        """Return the number of likes."""
        return self.likes.count()

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent_comment is not None


class CommentLike(models.Model):
    """
    Model to track likes on comments.
    """

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="comment_likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comment_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_comment_like"
        unique_together = ("comment", "user")
        verbose_name = "Comment Like"
        verbose_name_plural = "Comment Likes"

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"


class BookClub(models.Model):
    """
    Model to represent book clubs that users can join.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    # Club Management
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_clubs"
    )
    moderators = models.ManyToManyField(
        User, related_name="moderated_clubs", blank=True
    )
    members = models.ManyToManyField(
        User, through="BookClubMembership", related_name="book_clubs"
    )

    # Club Settings
    is_public = models.BooleanField(
        default=True, help_text="Can anyone join this club?"
    )
    max_members = models.IntegerField(
        null=True, blank=True, help_text="Maximum number of members (optional)"
    )

    # Current Book
    current_book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_in_clubs",
    )

    # Club Image
    club_image = models.ImageField(
        upload_to="club_images/", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_book_club"
        verbose_name = "Book Club"
        verbose_name_plural = "Book Clubs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Return the number of members."""
        return self.members.count()

    @property
    def is_full(self):
        """Check if the club has reached maximum capacity."""
        if self.max_members:
            return self.member_count >= self.max_members
        return False


class BookClubMembership(models.Model):
    """
    Model to track book club memberships.
    """

    ROLE_CHOICES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    ]

    club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="member"
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "social_book_club_membership"
        unique_together = ("club", "user")
        verbose_name = "Book Club Membership"
        verbose_name_plural = "Book Club Memberships"

    def __str__(self):
        return f"{self.user.username} in {self.club.name} ({self.role})"


class BookClubDiscussion(models.Model):
    """
    Model to represent discussions within book clubs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        BookClub, on_delete=models.CASCADE, related_name="discussions"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="club_discussions"
    )

    # Related Book (optional)
    related_book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="club_discussions",
    )

    # Discussion Settings
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_book_club_discussion"
        verbose_name = "Book Club Discussion"
        verbose_name_plural = "Book Club Discussions"
        ordering = ["-is_pinned", "-updated_at"]

    def __str__(self):
        return f"{self.title} in {self.club.name}"


class BookClubDiscussionReply(models.Model):
    """
    Model to represent replies to book club discussions.
    """

    discussion = models.ForeignKey(
        BookClubDiscussion, on_delete=models.CASCADE, related_name="replies"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="club_replies"
    )
    content = models.TextField()

    # Reply to another reply
    parent_reply = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_replies",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_book_club_discussion_reply"
        verbose_name = "Book Club Discussion Reply"
        verbose_name_plural = "Book Club Discussion Replies"
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.author.username} in {self.discussion.title}"


class DirectMessage(models.Model):
    """
    Model to represent direct messages between users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )

    content = models.TextField()

    # Message Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Related Objects (optional)
    related_book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_messages",
    )
    related_barter_request = models.ForeignKey(
        "barter.BarterRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_messages",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_direct_message"
        verbose_name = "Direct Message"
        verbose_name_plural = "Direct Messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender"]),
            models.Index(fields=["recipient"]),
            models.Index(fields=["is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"Message from {self.sender.username} to {self.recipient.username}"
        )


class UserActivity(models.Model):
    """
    Model to track user activities for the activity feed.
    This works alongside django-activity-stream.
    """

    ACTIVITY_TYPE_CHOICES = [
        ("book_added", "Added a Book"),
        ("book_reviewed", "Reviewed a Book"),
        ("post_created", "Created a Post"),
        ("barter_completed", "Completed a Barter"),
        ("club_joined", "Joined a Book Club"),
        ("user_followed", "Followed a User"),
        ("reading_started", "Started Reading"),
        ("reading_finished", "Finished Reading"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activities"
    )
    activity_type = models.CharField(
        max_length=20, choices=ACTIVITY_TYPE_CHOICES
    )
    description = models.CharField(max_length=200)

    # Related Objects (generic foreign keys would be better, but keeping simple)
    related_book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, null=True, blank=True
    )
    related_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="related_activities",
    )
    related_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True
    )

    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_user_activity"
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class Recommendation(models.Model):
    """
    Model to represent book recommendations between users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_recommendations"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_recommendations"
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="recommendations"
    )

    message = models.TextField(help_text="Why are you recommending this book?")

    # Recipient Response
    is_read = models.BooleanField(default=False)
    is_accepted = models.BooleanField(
        null=True, blank=True
    )  # True=accepted, False=declined, None=no response
    response_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "social_recommendation"
        verbose_name = "Book Recommendation"
        verbose_name_plural = "Book Recommendations"
        unique_together = ("recommender", "recipient", "book")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recommender.username} recommends {self.book.title} to {self.recipient.username}"
