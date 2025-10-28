from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from social.models import Post
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class CreatePostTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.client.login(username="testuser", password="password123")  # authenticate the client
        self.url = "/posts/create/"

    def test_create_post_success(self):
        data = {
            "content": "This is my first post!",
            "post_type": "text",
            "is_public": True
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().content, "This is my first post!")

    def test_create_post_unauthenticated(self):
        self.client.logout()
        data = {"content": "No login post"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
