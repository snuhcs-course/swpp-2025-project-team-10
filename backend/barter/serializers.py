"""
Serializers for the barter app.
"""

from accounts.serializers import UserBarterInfoSerializer
from books.serializers import BookSummarySerializer
from rest_framework import serializers

from .models import BarterRequest


class BarterRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for BarterRequest with requester/recipient info.
    New flow: requester proposes 3 books (offered_book_ids) for recipient's 1 book (requested_book).
    Emails are only exposed when status is 'completed'.
    """

    requester = UserBarterInfoSerializer(read_only=True)
    recipient = UserBarterInfoSerializer(read_only=True)
    offered_book = BookSummarySerializer(
        read_only=True
    )  # The selected book after acceptance
    requested_book = BookSummarySerializer(read_only=True)
    offered_book_ids = serializers.ListField(
        child=serializers.UUIDField(),
        read_only=True,
        help_text="List of 3 book IDs proposed by requester",
    )

    # Emails only visible when trade is completed
    requester_email = serializers.SerializerMethodField()
    recipient_email = serializers.SerializerMethodField()

    class Meta:
        model = BarterRequest
        fields = [
            "id",
            "requester",
            "recipient",
            "offered_book",  # The final selected book (set after acceptance)
            "offered_book_ids",  # The 3 proposed books
            "requested_book",
            "message",
            "status",
            "preferred_meeting_type",
            "proposed_meeting_location",
            "proposed_meeting_time",
            "response_message",
            "response_date",
            "requester_email",
            "recipient_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requester",
            "recipient",
            "offered_book",
            "offered_book_ids",
            "status",
            "response_date",
            "requester_email",
            "recipient_email",
            "created_at",
            "updated_at",
        ]

    def get_requester_email(self, obj):
        """Return requester's email only if trade is completed."""
        if obj.status == "completed":
            return obj.requester.email
        return None

    def get_recipient_email(self, obj):
        """Return recipient's email only if trade is completed."""
        if obj.status == "completed":
            return obj.recipient.email
        return None


class BarterAcceptSerializer(serializers.Serializer):
    """
    Serializer for accepting a barter request.
    """

    response_message = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )
    proposed_meeting_time = serializers.DateTimeField(
        required=False, allow_null=True
    )
    proposed_meeting_location = serializers.CharField(
        required=False, allow_blank=True, max_length=200
    )


class BarterRejectSerializer(serializers.Serializer):
    """
    Serializer for rejecting a barter request.
    """

    response_message = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )


class BarterCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new barter request.
    Requester just selects recipient's book, backend automatically picks 3 of requester's books.
    """

    requested_book_id = serializers.UUIDField(
        required=True,
        help_text="ID of the book that requester wants from recipient",
    )
