from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image


class BookGenre(models.TextChoices):
    NOVEL = "NOVEL", "소설"
    ESSAY = "ESSAY", "에세이"
    POETRY = "POETRY", "시"
    SELF_HELP = "SELF_HELP", "자기계발"
    SCIENCE_TECH = "SCIENCE_TECH", "과학·기술"
    HUMANITIES_SOCIAL = "HUMANITIES_SOCIAL", "인문·사회"
    HISTORY_PHILOSOPHY = "HISTORY_PHILOSOPHY", "역사·철학"
    ART_LANGUAGE = "ART_LANGUAGE", "예술·언어"
    ECONOMICS_BUSINESS = "ECONOMICS_BUSINESS", "경제·경영"


class Author(models.TextChoices):
    HAN_KANG = "HAN_KANG", "한강"
    KIM_YOUNG_HA = "KIM_YOUNG_HA", "김영하"
    JUNG_JAE_SEUNG = "JUNG_JAE_SEUNG", "정재승"
    MURAKAMI_HARUKI = "MURAKAMI_HARUKI", "무라카미 하루키"
    F_SCOTT_FITZGERALD = "F_SCOTT_FITZGERALD", "F. 스콧 피츠제럴드"
    YUVAL_HARARI = "YUVAL_HARARI", "유발 하라리"
    BERNARD_WERBER = "BERNARD_WERBER", "베르나르 베르베르"
    NIETZSCHE = "NIETZSCHE", "프리드리히 니체"
    SAGAN = "SAGAN", "칼 세이건"


class Book(models.TextChoices):
    DEMIAN = "DEMIAN", "데미안"
    SAPIENS = "SAPIENS", "사피엔스"
    NINETEEN_EIGHTY_FOUR = "1984", "1984"
    VEGETARIAN = "VEGETARIAN", "채식주의자"
    COSMOS = "COSMOS", "코스모스"
    MILLIONAIRE_FASTLANE = "MILLIONAIRE_FASTLANE", "부의 추월차선"
    WHEN_BREATH_BECOMES_AIR = "WHEN_BREATH_BECOMES_AIR", "숨결이 바람 될 때"
    CONVENIENCE_STORE = "CONVENIENCE_STORE", "불편한 편의점"
    HOW_TO_LIVE = "HOW_TO_LIVE", "어떻게 살 것인가"


class BookLength(models.TextChoices):
    SHORT = "SHORT", "짧음"
    MEDIUM = "MEDIUM", "보통"
    LONG = "LONG", "두꺼움"


class BookMood(models.TextChoices):
    WARM = "WARM", "따뜻한"
    SERIOUS = "SERIOUS", "진지한"
    HUMOROUS = "HUMOROUS", "유머러스한"
    TOUCHING = "TOUCHING", "감동적인"
    IMMERSIVE = "IMMERSIVE", "몰입감 있는"
    CALM = "CALM", "차분한"
    MYSTERIOUS = "MYSTERIOUS", "신비로운"
    SHARP = "SHARP", "날카로운"
    ENERGETIC = "ENERGETIC", "활기찬"


class ReadingPurpose(models.TextChoices):
    STUDY = "STUDY", "공부 / 지식 습득을 위해서"
    HEALING = "HEALING", "힐링 및 휴식을 위해서"
    INSPIRATION = "INSPIRATION", "영감을 얻기 위해서"
    LIGHT_READING = "LIGHT_READING", "가볍게 즐기기 위해서"
    DEEP_READING = "DEEP_READING", "깊이 있게 몰입하기 위해서"
    NEW_PERSPECTIVE = "NEW_PERSPECTIVE", "새로운 관점을 얻기 위해서"
    CULTURE = "CULTURE", "교양 및 상식을 쌓기 위해서"
    PROBLEM_SOLVING = "PROBLEM_SOLVING", "특정 문제의 답을 찾기 위해서"
    ESCAPISM = "ESCAPISM", "현실 도피 및 상상의 확장을 위해서"


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
    bio = models.TextField(
        max_length=500, blank=True, help_text="Tell others about yourself"
    )
    location = models.CharField(
        max_length=100, blank=True, help_text="Your city or region"
    )
    birth_date = models.DateField(null=True, blank=True)

    # Profile Picture
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        help_text="Upload a profile picture",
    )

    # Contact Information
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )

    # Profile visibility & messaging
    is_profile_public = models.BooleanField(
        default=True, help_text="Make your profile visible to other users"
    )

    allow_direct_messages = models.BooleanField(
        default=True, help_text="Allow other users to send you direct messages"
    )

    # Reputation / activity metrics
    reputation_score = models.IntegerField(default=0)
    successful_trades = models.IntegerField(default=0)

    # Social Features
    followers = models.ManyToManyField(
        "self", through="Follow", related_name="following", symmetrical=False
    )

    # User Taste Information #(가입할때만 하게. skip하고 싶을수도있으니까)
    has_initial_taste = models.BooleanField(default=False)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Keep last_active in sync with initial migration (auto-updated)
    last_active = models.DateTimeField(auto_now=True)

    # Email as username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's first name."""
        return self.first_name

    def save(self, *args, **kwargs):
        """Override save to resize profile picture if set."""
        super().save(*args, **kwargs)

        if self.profile_picture:
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception:
                # don't crash user save on image processing errors
                pass

    @property
    def follower_count(self):
        """Return the number of followers."""
        return self.follower_relationships.count()

    @property
    def following_count(self):
        """Return the number of users this user is following."""
        return self.following_relationships.count()

    @property
    def post_count(self):
        """Return the number of posts this user has created."""
        return self.posts.count()


class UserTaste(models.Model):
    """
    Model to store user's book preferences and taste information.
    This model holds the six-step initial taste survey as JSON lists so the
    frontend can walk the user through steps and update progressively.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="taste"
    )

    # Step 1: Genre preferences (list of BookGenre keys)
    favorite_genres = models.JSONField(
        default=list, help_text="List of favorite book genres (keys)"
    )

    # Step 2: Author preferences (list of Author keys)
    favorite_authors = models.JSONField(
        default=list, help_text="List of favorite authors (keys)"
    )

    # Step 3: Book preferences (list of Book keys)
    favorite_books = models.JSONField(
        default=list, help_text="List of favorite books (keys)"
    )

    # Step 4: Book length preference (single choice)
    preferred_length = models.CharField(
        max_length=20,
        choices=BookLength.choices,
        null=True,
        blank=True,
    )

    # Step 5: Book mood preferences (list of BookMood keys)
    preferred_moods = models.JSONField(
        default=list, help_text="List of preferred book moods (keys)"
    )

    # Step 6: Reading purposes (list of ReadingPurpose keys)
    reading_purposes = models.JSONField(
        default=list, help_text="List of reading purposes (keys)"
    )

    # Step 7: Trade style (location and place)
    trade_place_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Preferred trade place name (e.g., cafe, library)",
    )
    trade_address = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preferred trade address (optional)",
    )

    # Categorization progress (1..7)
    current_step = models.IntegerField(
        default=1, help_text="Current categorization step (1-7)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Taste"
        verbose_name_plural = "User Tastes"

    def __str__(self):
        return (
            f"{self.user.username}'s taste profile - Step {self.current_step}"
        )


class Follow(models.Model):
    """
    Model to represent follow relationships between users.
    """

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following_relationships"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower_relationships"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        db_table = "accounts_follow"
        verbose_name = "Follow Relationship"
        verbose_name_plural = "Follow Relationships"

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class UserPreferences(models.Model):
    """
    Model to store user preferences and settings.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )

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
        default=50, help_text="Maximum distance (in km) for book bartering"
    )
    preferred_meeting_locations = models.TextField(
        blank=True, help_text="Preferred locations for book exchanges"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_user_preferences"
        verbose_name = "User Preferences"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"{self.user.username}'s preferences"
