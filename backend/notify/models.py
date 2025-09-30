from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

User = get_user_model()


class Notification(models.Model):
    """
    Custom notification model to extend django-notifications-hq.
    """

    NOTIFICATION_TYPE_CHOICES = [
        ('barter_request', 'Barter Request'),
        ('barter_accepted', 'Barter Accepted'),
        ('barter_rejected', 'Barter Rejected'),
        ('barter_completed', 'Barter Completed'),
        ('message_received', 'Message Received'),
        ('post_liked', 'Post Liked'),
        ('comment_received', 'Comment Received'),
        ('user_followed', 'User Followed'),
        ('book_recommended', 'Book Recommended'),
        ('club_invitation', 'Club Invitation'),
        ('club_discussion', 'Club Discussion'),
        ('system_announcement', 'System Announcement'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )

    # Notification Details
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    # Related Object (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Delivery
    is_email_sent = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notify_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """
    Model to store user notification preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Email Notifications
    email_barter_requests = models.BooleanField(default=True)
    email_barter_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_social_activity = models.BooleanField(default=False)
    email_recommendations = models.BooleanField(default=True)
    email_club_activity = models.BooleanField(default=True)
    email_system_announcements = models.BooleanField(default=True)

    # Push Notifications
    push_barter_requests = models.BooleanField(default=True)
    push_barter_updates = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_social_activity = models.BooleanField(default=True)
    push_recommendations = models.BooleanField(default=True)
    push_club_activity = models.BooleanField(default=True)
    push_system_announcements = models.BooleanField(default=True)

    # In-App Notifications
    inapp_barter_requests = models.BooleanField(default=True)
    inapp_barter_updates = models.BooleanField(default=True)
    inapp_messages = models.BooleanField(default=True)
    inapp_social_activity = models.BooleanField(default=True)
    inapp_recommendations = models.BooleanField(default=True)
    inapp_club_activity = models.BooleanField(default=True)
    inapp_system_announcements = models.BooleanField(default=True)

    # Frequency Settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Never'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )

    # Quiet Hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notify_notification_preference'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class NotificationTemplate(models.Model):
    """
    Model to store notification templates for different types.
    """
    notification_type = models.CharField(
        max_length=30,
        choices=Notification.NOTIFICATION_TYPE_CHOICES,
        unique=True
    )

    # Templates
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=200, blank=True)
    email_body_template = models.TextField(blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    default_priority = models.CharField(
        max_length=10,
        choices=Notification.PRIORITY_CHOICES,
        default='normal'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notify_notification_template'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'

    def __str__(self):
        return f"Template for {self.get_notification_type_display()}"


class NotificationBatch(models.Model):
    """
    Model to track batch notifications (like system announcements).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Targeting
    target_all_users = models.BooleanField(default=False)
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_batches')

    # Status
    is_sent = models.BooleanField(default=False)
    sent_count = models.IntegerField(default=0)

    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_batches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notify_notification_batch'
        verbose_name = 'Notification Batch'
        verbose_name_plural = 'Notification Batches'
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch: {self.title}"
