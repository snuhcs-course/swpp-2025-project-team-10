from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_id = serializers.IntegerField(source='recipient.id', read_only=True)
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id',
            'recipient',
            'sender',
            'notification_type',
            'title',
            'message',
            'is_read',
            'created_at',
        )
