import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher
from social.models import Post
from notify.models import Notification


User = get_user_model()


@pytest.mark.django_db
def test_like_and_comment_and_barter_create_notifications():
    client = APIClient()
    author = User.objects.create(username="author", email="a@example.com", first_name="A", last_name="U")
    actor = User.objects.create(username="actor", email="x@example.com", first_name="X", last_name="Y")

    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(title="T", owner=author, publisher=publisher)
    book.authors.add(auth)

    post = Post.objects.create(author=author, content="hello", related_book=book)

    # like
    client.force_authenticate(actor)
    res = client.post(f"/posts/{post.id}/like/")
    assert res.status_code == 200
    assert Notification.objects.filter(recipient=author, notification_type="post_liked").exists()

    # comment
    res = client.post(f"/posts/{post.id}/comments/", {"content": "nice"}, format="json")
    assert res.status_code == 201
    assert Notification.objects.filter(recipient=author, notification_type="comment_received").exists()

    # barter
    res = client.post(f"/posts/{post.id}/barter/", {}, format="json")
    assert res.status_code == 201
    assert Notification.objects.filter(recipient=author, notification_type="barter_request").exists()
    payload = res.data["barter"]
    assert payload["requester"]["username"] == "actor"
    assert payload["requestedBook"]["id"] == str(book.id)
