from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    # 프론트엔드 DTO에 맞춰서 필드명 변경
    body = serializers.CharField(source="message", read_only=True)
    type = serializers.CharField(source="notification_type", read_only=True)
    deepLink = serializers.SerializerMethodField()
    related_object_id = serializers.CharField(
        source="object_id", read_only=True
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "body",  # message -> body
            "created_at",
            "is_read",
            "deepLink",  # 딥링크
            "type",  # notification_type -> type
            "related_object_id",  # barter request id, post id 등
        )

    def get_deepLink(self, obj):
        """
        알림 타입과 관련 객체에 따라 딥링크 생성
        """
        if not obj.content_object or not obj.object_id:
            return None

        # 알림 타입별로 딥링크 생성
        if obj.notification_type in [
            'barter_request', 
            'barter_request_sent', 
            'barter_accepted', 
            'barter_rejected', 
            'barter_completed', 
            'barter_counter_proposed'
        ]:
            return f"app://barter/{obj.object_id}"
        elif obj.notification_type in ["post_liked", "comment_received"]:
            return f"app://post/{obj.object_id}"
        elif obj.notification_type == "user_followed":
            return f"app://profile/{obj.object_id}"
        elif obj.notification_type == "club_invitation":
            return f"app://club/{obj.object_id}"

        return None
