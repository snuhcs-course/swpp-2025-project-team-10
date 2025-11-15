# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from notifications.models import Notification

class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        Notification.objects.create(user=self.user, message='New barter request!')

    def test_list_notifications(self):
        response = self.client.get('/api/v1/notifications/list/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_read(self):
        notif = Notification.objects.first()
        response = self.client.post(f'/api/v1/notifications/{notif.id}/mark-read/')
        self.assertEqual(response.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
