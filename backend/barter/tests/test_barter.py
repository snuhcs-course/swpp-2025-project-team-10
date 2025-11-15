from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from barter.models import Barter, Notification

class BarterTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.client.login(username='user1', password='pass')

    def test_create_barter_request(self):
        response = self.client.post('/api/v1/barter/request/', {'to_user': self.user2.id})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Barter.objects.filter(created_by=self.user1, created_for=self.user2).exists())

    def test_duplicate_barter_request(self):
        Barter.objects.create(created_by=self.user1, created_for=self.user2, status='pending')
        response = self.client.post('/api/v1/barter/request/', {'to_user': self.user2.id})
        self.assertEqual(response.status_code, 400)

    def test_accept_barter_creates_notification(self):
        barter = Barter.objects.create(created_by=self.user1, created_for=self.user2, status='pending')
        self.client.login(username='user2', password='pass')
        response = self.client.post(f'/api/v1/barter/{barter.id}/accept/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Notification.objects.filter(user=self.user1, message__contains='accepted').exists())
