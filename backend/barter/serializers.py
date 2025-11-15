"""
Serializers for the barter app.
"""

from rest_framework import serializers

from accounts.serializers import UserBarterInfoSerializer
from books.serializers import BookSummarySerializer

from .models import BarterRequest


class BarterRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for BarterRequest with requester/recipient info.
    1:1 exchange - single offered_book and single requested_book.
    Phone numbers are only exposed when status is 'completed'.
    """

    requester = UserBarterInfoSerializer(read_only=True)
    recipient = UserBarterInfoSerializer(read_only=True)
    offered_book = BookSummarySerializer(read_only=True)
    requested_book = BookSummarySerializer(read_only=True)
    
    # Phone numbers only visible when trade is completed
    requester_phone = serializers.SerializerMethodField()
    recipient_phone = serializers.SerializerMethodField()

    class Meta:
        model = BarterRequest
        fields = [
            "id",
            "requester",
            "recipient",
            "offered_book",
            "requested_book",
            "message",
            "status",
            "preferred_meeting_type",
            "proposed_meeting_location",
            "proposed_meeting_time",
            "response_message",
            "response_date",
            "requester_phone",
            "recipient_phone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requester",
            "recipient",
            "status",
            "response_date",
            "requester_phone",
            "recipient_phone",
            "created_at",
            "updated_at",
        ]

    def get_requester_phone(self, obj):
        """Return requester's phone only if trade is completed."""
        if obj.status == "completed":
            return obj.requester.phone_number
        return None

    def get_recipient_phone(self, obj):
        """Return recipient's phone only if trade is completed."""
        if obj.status == "completed":
            return obj.recipient.phone_number
        return None


class BarterAcceptSerializer(serializers.Serializer):
    """
    Serializer for accepting a barter request.
    """

    response_message = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )
    proposed_meeting_time = serializers.DateTimeField(required=False, allow_null=True)
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
