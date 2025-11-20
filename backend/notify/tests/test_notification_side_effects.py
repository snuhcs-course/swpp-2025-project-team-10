import pytest
from books.models import Author as BookAuthor
from books.models import (
    BookCopy,
    BookPublication,
    Publisher,
)
from django.contrib.auth import get_user_model
from notify.models import Notification
from rest_framework.test import APIClient
from social.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_notifications_on_user_actions():
    client = APIClient()
    author = User.objects.create(
        username="author", email="a@example.com", first_name="A", last_name="U"
    )
    actor = User.objects.create(
        username="actor", email="x@example.com", first_name="X", last_name="Y"
    )

    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    publication = BookPublication.objects.create(
        title="T", publisher=publisher
    )
    publication.authors.add(auth)
    book = BookCopy.objects.create(publication=publication, owner=author)

    post = Post.objects.create(
        author=author, content="hello", related_book=book
    )

    client.force_authenticate(actor)

    # wishlist should notify the book owner
    res = client.post(f"/library/books/{book.id}/wishlist/")
    assert res.status_code == 200
    assert Notification.objects.filter(
        recipient=author, notification_type="book_wishlisted"
    ).exists()

    # like
    client.post(f"/posts/{post.id}/like/")
    assert Notification.objects.filter(
        recipient=author, notification_type="post_liked"
    ).exists()

    # comment
    client.post(
        f"/posts/{post.id}/comments/", {"content": "hi"}, format="json"
    )
    assert Notification.objects.filter(
        recipient=author, notification_type="comment_received"
    ).exists()

    # barter - actor must offer a book they own
    actor_book = BookCopy.objects.create(
        publication=publication, owner=actor, is_for_barter=True
    )
    client.post(
        f"/posts/{post.id}/barter/",
        {"offered_book_id": str(actor_book.id)},
        format="json",
    )
    assert Notification.objects.filter(
        recipient=author, notification_type="barter_request"
    ).exists()
