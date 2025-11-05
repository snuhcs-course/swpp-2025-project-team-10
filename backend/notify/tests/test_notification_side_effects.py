import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher
from social.models import Post
from notify.models import Notification


User = get_user_model()


@pytest.mark.django_db
def test_notifications_on_user_actions():
    client = APIClient()
    author = User.objects.create(username="author", email="a@example.com", first_name="A", last_name="U")
    actor = User.objects.create(username="actor", email="x@example.com", first_name="X", last_name="Y")

    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(title="T", owner=author, publisher=publisher)
    book.authors.add(auth)

    post = Post.objects.create(author=author, content="hello", related_book=book)

    client.force_authenticate(actor)

    # wishlist self-notification
    res = client.post(f"/library/books/{book.id}/wishlist/")
    assert res.status_code == 200
    assert Notification.objects.filter(recipient=actor, notification_type="book_wishlisted").exists()

    # like
    client.post(f"/posts/{post.id}/like/")
    assert Notification.objects.filter(recipient=author, notification_type="post_liked").exists()

    # comment
    client.post(f"/posts/{post.id}/comments/", {"content": "hi"}, format="json")
    assert Notification.objects.filter(recipient=author, notification_type="comment_received").exists()

    # barter
    client.post(f"/posts/{post.id}/barter/", {})
    assert Notification.objects.filter(recipient=author, notification_type="barter_request").exists()
