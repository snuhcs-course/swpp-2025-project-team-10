from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User, UserPreferences, UserTaste


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model.
    """

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_profile_public",
        "reputation_score",
        "successful_trades",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_profile_public",
        "allow_direct_messages",
        "date_joined",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Profile Information",
            {
                "fields": (
                    "bio",
                    "location",
                    "birth_date",
                    "profile_picture",
                    "phone_number",
                )
            },
        ),
        (
            "Privacy Settings",
            {"fields": ("is_profile_public", "allow_direct_messages")},
        ),
        (
            "Reputation",
            {
                "fields": ("reputation_score", "successful_trades"),
                "classes": ("collapse",),
            },
        ),
        ("Activity", {"fields": ("last_active",), "classes": ("collapse",)}),
    )

    readonly_fields = ("reputation_score", "successful_trades", "last_active")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Admin configuration for Follow relationships.
    """

    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")
    raw_id_fields = ("follower", "following")
    ordering = ("-created_at",)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Admin configuration for User Preferences.
    """

    list_display = (
        "user",
        "email_notifications",
        "push_notifications",
        "max_barter_distance",
    )
    list_filter = (
        "email_notifications",
        "push_notifications",
        "barter_request_notifications",
        "message_notifications",
        "follow_notifications",
    )
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Notification Preferences",
            {
                "fields": (
                    "email_notifications",
                    "push_notifications",
                    "barter_request_notifications",
                    "message_notifications",
                    "follow_notifications",
                )
            },
        ),
        (
            "Privacy Preferences",
            {"fields": ("show_email", "show_phone", "show_location")},
        ),
        (
            "Barter Preferences",
            {"fields": ("max_barter_distance", "preferred_meeting_locations")},
        ),
    )


@admin.register(UserTaste)
class UserTasteAdmin(admin.ModelAdmin):
    """
    Admin configuration for User Taste.
    """

    list_display = ("user", "current_step", "trade_place_name", "trade_address")
    search_fields = ("user__username", "trade_place_name", "trade_address")
    list_filter = ("current_step",)
    readonly_fields = ("user",)
