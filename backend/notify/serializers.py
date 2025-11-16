from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    # 프론트엔드 DTO에 맞춰서 필드명 변경
    body = serializers.CharField(source='message', read_only=True)
    type = serializers.CharField(source='notification_type', read_only=True)
    deepLink = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'title',
            'body',           # message -> body
            'created_at',
            'is_read',
            'deepLink',       # 새로 추가
            'type',           # notification_type -> type
        )
    
    def get_deepLink(self, obj):
        """
        알림 타입에 따라 딥링크 생성
        나중에 필요하면 구현 가능
        """
        return None
