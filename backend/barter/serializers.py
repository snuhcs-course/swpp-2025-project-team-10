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
    """

    requester = UserBarterInfoSerializer(read_only=True)
    recipient = UserBarterInfoSerializer(read_only=True)
    offered_books = BookSummarySerializer(many=True, read_only=True)
    requested_books = BookSummarySerializer(many=True, read_only=True)

    class Meta:
        model = BarterRequest
        fields = [
            "id",
            "requester",
            "recipient",
            "offered_books",
            "requested_books",
            "message",
            "status",
            "preferred_meeting_type",
            "proposed_meeting_location",
            "proposed_meeting_time",
            "response_message",
            "response_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requester",
            "recipient",
            "status",
            "response_date",
            "created_at",
            "updated_at",
        ]


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
