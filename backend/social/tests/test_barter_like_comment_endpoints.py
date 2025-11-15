import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher
from social.models import Post, PostLike, Comment
from barter.models import BarterRequest
from notify.models import Notification


User = get_user_model()


@pytest.mark.django_db
def test_like_and_comment_and_barter_create_notifications():
    client = APIClient()
    author = User.objects.create(username="author", email="a@example.com", first_name="A", last_name="U")
    actor = User.objects.create(username="actor", email="x@example.com", first_name="X", last_name="Y")

    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(title="T", owner=author, publisher=publisher, is_for_barter=True, trade_status="available")
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

    # barter - initial request (no offered_book yet in 2-step flow)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "I want to trade for your book!"},
        format="json",
    )
    assert res.status_code == 201
    assert Notification.objects.filter(recipient=author, notification_type="barter_request").exists()
    payload = res.data["barter"]
    assert payload["requester"]["username"] == "actor"
    assert payload["requested_book"]["id"] == str(book.id)


# Error cases for comment


@pytest.mark.django_db
def test_comment_post_without_content():
    """Test commenting with missing content."""
    client = APIClient()
    author = User.objects.create(username="author_comment", email="ac@test.com", first_name="A", last_name="User")
    commenter = User.objects.create(username="commenter", email="c@test.com", first_name="C", last_name="User")
    
    post = Post.objects.create(author=author, content="Test post", is_public=True)
    
    client.force_authenticate(commenter)
    res = client.post(f"/posts/{post.id}/comments/", {}, format="json")
    
    assert res.status_code == 400


@pytest.mark.django_db
def test_comment_post_with_empty_content():
    """Test commenting with empty content."""
    client = APIClient()
    author = User.objects.create(username="author_ec", email="aec@test.com", first_name="A", last_name="User")
    commenter = User.objects.create(username="commenter_ec", email="cec@test.com", first_name="C", last_name="User")
    
    post = Post.objects.create(author=author, content="Test post", is_public=True)
    
    client.force_authenticate(commenter)
    res = client.post(
        f"/posts/{post.id}/comments/",
        {"content": ""},
        format="json",
    )
    
    assert res.status_code == 400


@pytest.mark.django_db
def test_comment_nonexistent_post():
    """Test commenting on a nonexistent post."""
    client = APIClient()
    user = User.objects.create(username="commenter_ne", email="cne@test.com", first_name="C", last_name="User")
    
    client.force_authenticate(user)
    fake_uuid = uuid.uuid4()
    res = client.post(
        f"/posts/{fake_uuid}/comments/",
        {"content": "Comment"},
        format="json",
    )
    
    assert res.status_code == 404


# Error cases for barter


@pytest.mark.django_db
def test_barter_post_without_related_book():
    """Test barter on post without related_book."""
    client = APIClient()
    author = User.objects.create(username="author_nb", email="anb@test.com", first_name="A", last_name="User")
    requester = User.objects.create(username="req_nb", email="rnb@test.com", first_name="R", last_name="User")
    
    post = Post.objects.create(author=author, content="Just a post", is_public=True)
    
    client.force_authenticate(requester)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "Trade?"},
        format="json",
    )
    
    assert res.status_code == 400
    # Check that error message mentions book or related_book
    error_msg = str(res.data).lower()
    assert "book" in error_msg


@pytest.mark.django_db
def test_barter_post_not_found():
    """Test barter on nonexistent post."""
    client = APIClient()
    user = User.objects.create(username="req_nf", email="rnf@test.com", first_name="R", last_name="User")
    
    client.force_authenticate(user)
    fake_uuid = uuid.uuid4()
    res = client.post(
        f"/posts/{fake_uuid}/barter/",
        {"message": "Trade?"},
        format="json",
    )
    
    assert res.status_code == 404


@pytest.mark.django_db
def test_barter_own_book():
    """Test user cannot barter their own book."""
    client = APIClient()
    owner = User.objects.create(username="owner_own", email="oo@test.com", first_name="O", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub_own")
    auth = BookAuthor.objects.create(name="Auth_own")
    book = Book.objects.create(
        title="MyBook",
        owner=owner,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    post = Post.objects.create(author=owner, content="Offering book", related_book=book, is_public=True)
    
    client.force_authenticate(owner)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "I want my own book?"},
        format="json",
    )
    
    # Returns 403 (Forbidden) when trying to barter own book
    assert res.status_code == 403
    assert "own" in str(res.data).lower()


@pytest.mark.django_db
def test_barter_book_not_for_barter():
    """Test cannot barter book not marked for barter."""
    client = APIClient()
    owner = User.objects.create(username="owner_nb", email="onb@test.com", first_name="O", last_name="User")
    requester = User.objects.create(username="req_nb2", email="rnb2@test.com", first_name="R", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub_nb")
    auth = BookAuthor.objects.create(name="Auth_nb")
    book = Book.objects.create(
        title="NotForBarter",
        owner=owner,
        publisher=publisher,
        is_for_barter=False,  # Not for barter
        trade_status="not_available"
    )
    book.authors.add(auth)
    
    post = Post.objects.create(author=owner, content="Just showing", related_book=book, is_public=True)
    
    client.force_authenticate(requester)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "Can I trade?"},
        format="json",
    )
    
    assert res.status_code == 400
    assert "not available" in str(res.data).lower() or "barter" in str(res.data).lower()


@pytest.mark.django_db
def test_barter_book_already_in_trade():
    """Test cannot barter book already in trade."""
    client = APIClient()
    owner = User.objects.create(username="owner_trade", email="ot@test.com", first_name="O", last_name="User")
    requester = User.objects.create(username="req_trade", email="rt@test.com", first_name="R", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub_trade")
    auth = BookAuthor.objects.create(name="Auth_trade")
    book = Book.objects.create(
        title="InTrade",
        owner=owner,
        publisher=publisher,
        is_for_barter=True,
        trade_status="not_available"  # Already in trade
    )
    book.authors.add(auth)
    
    post = Post.objects.create(author=owner, content="Offering book", related_book=book, is_public=True)
    
    client.force_authenticate(requester)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "Can I trade?"},
        format="json",
    )
    
    assert res.status_code == 400
    assert "not available" in str(res.data).lower() or "trade" in str(res.data).lower()


# Success cases


@pytest.mark.django_db
def test_like_post_toggle():
    """Test like_post view for liking and unliking."""
    client = APIClient()
    author = User.objects.create(username="author2", email="a2@test.com", first_name="A", last_name="User")
    liker = User.objects.create(username="liker2", email="l2@test.com", first_name="L", last_name="User")
    
    post = Post.objects.create(author=author, content="Test post", is_public=True)
    
    client.force_authenticate(liker)
    
    # Like the post
    res = client.post(f"/posts/{post.id}/like/")
    assert res.status_code == 200
    assert PostLike.objects.filter(post=post, user=liker).exists()
    
    # Notification should be created
    assert Notification.objects.filter(
        recipient=author,
        sender=liker,
        notification_type="post_liked"
    ).exists()
    
    # Unlike the post
    res = client.post(f"/posts/{post.id}/like/")
    assert res.status_code == 200
    assert not PostLike.objects.filter(post=post, user=liker).exists()


@pytest.mark.django_db
def test_comment_post_creates_comment():
    """Test comment_post view creates comment."""
    client = APIClient()
    author = User.objects.create(username="author3", email="a3@test.com", first_name="A", last_name="User")
    commenter = User.objects.create(username="comm2", email="c2@test.com", first_name="C", last_name="User")
    
    post = Post.objects.create(author=author, content="Test post", is_public=True)
    
    client.force_authenticate(commenter)
    res = client.post(
        f"/posts/{post.id}/comments/",
        {"content": "Nice post!"},
        format="json",
    )
    
    assert res.status_code == 201
    assert Comment.objects.filter(post=post, author=commenter, content="Nice post!").exists()
    
    # Notification should be created
    assert Notification.objects.filter(
        recipient=author,
        sender=commenter,
        notification_type="comment_received"
    ).exists()


@pytest.mark.django_db
def test_barter_post_creates_request():
    """Test barter_post view creates BarterRequest."""
    client = APIClient()
    owner = User.objects.create(username="owner2", email="o2@test.com", first_name="O", last_name="User")
    requester = User.objects.create(username="req2", email="r2@test.com", first_name="R", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub3")
    auth = BookAuthor.objects.create(name="Auth3")
    book = Book.objects.create(
        title="Book2",
        owner=owner,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    post = Post.objects.create(author=owner, content="Offering book", related_book=book, is_public=True)
    
    client.force_authenticate(requester)
    res = client.post(
        f"/posts/{post.id}/barter/",
        {"message": "I want this book!"},
        format="json",
    )
    
    assert res.status_code == 201
    assert "barter" in res.data
    
    # BarterRequest should be created
    barter = BarterRequest.objects.get(requester=requester, recipient=owner, requested_book=book)
    assert "I want this book!" in barter.message
    
    # Book should be marked as not_available
    book.refresh_from_db()
    assert book.trade_status == "not_available"
    
    # Notification should be created
    assert Notification.objects.filter(
        recipient=owner,
        sender=requester,
        notification_type="barter_request"
    ).exists()


@pytest.mark.django_db
def test_barter_post_auto_message_includes_location():
    """Test barter_post auto-generates message with location."""
    client = APIClient()
    owner = User.objects.create(username="owner3", email="o3@test.com", first_name="O", last_name="User")
    requester = User.objects.create(
        username="req3",
        email="r3@test.com",
        first_name="R",
        last_name="User",
        location="Seoul"
    )
    
    publisher = Publisher.objects.create(name="Pub4")
    auth = BookAuthor.objects.create(name="Auth4")
    book = Book.objects.create(
        title="Book3",
        owner=owner,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    post = Post.objects.create(author=owner, content="Offering book", related_book=book, is_public=True)
    
    client.force_authenticate(requester)
    # Don't provide custom message
    res = client.post(f"/posts/{post.id}/barter/", {}, format="json")
    
    assert res.status_code == 201
    
    barter = BarterRequest.objects.get(requester=requester, recipient=owner)
    # Auto-generated message should include location
    assert "Seoul" in barter.message
    assert book.title in barter.message
