from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image


class User(AbstractUser):
    """
    Custom User model for Book Bartering Social Network.

    Extends Django's AbstractUser to include additional fields
    for social networking and book bartering features.
    """

    # Basic Information
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Profile Information
    bio = models.TextField(max_length=500, blank=True, help_text="Tell others about yourself")
    location = models.CharField(max_length=100, blank=True, help_text="Your city or region")
    birth_date = models.DateField(null=True, blank=True)

    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Upload a profile picture"
    )

    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Social Features
    followers = models.ManyToManyField(
        'self',
        through='Follow',
        related_name='following',
        symmetrical=False,
        blank=True
    )

    # Book Preferences
    favorite_genres = models.ManyToManyField(
        'books.Genre',
        blank=True,
        related_name='users_who_like',
        help_text="Select your favorite book genres"
    )

    # Privacy Settings
    is_profile_public = models.BooleanField(
        default=True,
        help_text="Make your profile visible to other users"
    )
    allow_direct_messages = models.BooleanField(
        default=True,
        help_text="Allow other users to send you direct messages"
    )

    # Reputation System
    reputation_score = models.IntegerField(default=0)
    successful_trades = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    # Email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's first name."""
        return self.first_name

    def save(self, *args, **kwargs):
        """Override save to resize profile picture."""
        super().save(*args, **kwargs)

        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

    @property
    def follower_count(self):
        """Return the number of followers."""
        return self.followers.count()

    @property
    def following_count(self):
        """Return the number of users this user is following."""
        return self.following.count()

    @property
    def books_count(self):
        """Return the number of books owned by this user."""
        return self.books.count()


class Follow(models.Model):
    """
    Model to represent follow relationships between users.
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relationships'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        db_table = 'accounts_follow'
        verbose_name = 'Follow Relationship'
        verbose_name_plural = 'Follow Relationships'

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class UserPreferences(models.Model):
    """
    Model to store user preferences and settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')

    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    barter_request_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    follow_notifications = models.BooleanField(default=True)

    # Privacy Preferences
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)

    # Barter Preferences
    max_barter_distance = models.IntegerField(
        default=50,
        help_text="Maximum distance (in km) for book bartering"
    )
    preferred_meeting_locations = models.TextField(
        blank=True,
        help_text="Preferred locations for book exchanges"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"
