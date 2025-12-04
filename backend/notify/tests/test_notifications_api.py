import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.test import APIClient

from notify.models import Notification
from notify.serializers import NotificationSerializer

User = get_user_model()


@pytest.mark.django_db
def test_notifications_list_and_read():
    user = User.objects.create_user(
        username="noteuser", email="note@test.com", password="pw1234"
    )
    other = User.objects.create_user(
        username="other", email="other@test.com", password="pw1234"
    )
    content_type = ContentType.objects.get_for_model(user)
    notification = Notification.objects.create(
        recipient=user,
        sender=other,
        notification_type="user_followed",
        title="Follower",
        message="You have a new follower",
        content_type=content_type,
        object_id=str(other.id),
    )

    client = APIClient()
    client.force_authenticate(user=user)

    list_url = reverse("notifications")
    resp = client.get(list_url)
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload) == 1
    assert payload[0]["deepLink"] == f"app://profile/{other.id}"
    assert payload[0]["is_read"] is False

    read_url = reverse("read_notification", args=[notification.id])
    resp = client.patch(read_url)
    assert resp.status_code == 200
    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_notification_serializer_deeplink_variants():
    user = User.objects.create_user(
        username="serializer", email="ser@test.com", password="pw1234"
    )
    ct = ContentType.objects.get_for_model(user)

    barter_note = Notification(
        recipient=user,
        notification_type="barter_request",
        title="Barter",
        message="Barter incoming",
        content_type=ct,
        object_id=str(user.id),
    )
    post_note = Notification(
        recipient=user,
        notification_type="post_liked",
        title="Post liked",
        message="Someone liked your post",
        content_type=ct,
        object_id=str(user.id),
    )

    barter_data = NotificationSerializer(barter_note).data
    post_data = NotificationSerializer(post_note).data

    assert barter_data["deepLink"].startswith("app://barter/")
    assert post_data["deepLink"].startswith("app://post/")
