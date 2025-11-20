"""
Barter flow tests for the current 2-step exchange API:
1) requester proposes (auto-picks up to 3 of their available books)
2) recipient accepts one of the proposed books (or rejects)
"""

import pytest
from barter.models import BarterRequest
from books.models import Author as BookAuthor
from books.models import (
    BookCopy,
    BookPublication,
    Publisher,
)
from django.contrib.auth import get_user_model
from django.urls import reverse
from notify.models import Notification
from rest_framework.test import APIClient

User = get_user_model()


def make_copy(title, owner, publisher, author, **kwargs):
    publication = BookPublication.objects.create(
        title=title, publisher=publisher
    )
    publication.authors.add(author)
    return BookCopy.objects.create(
        publication=publication,
        owner=owner,
        **kwargs,
    )


@pytest.fixture
def setup_users_and_books():
    user_a = User.objects.create(
        username="user_a",
        email="a@test.com",
        first_name="A",
        last_name="User",
    )
    user_b = User.objects.create(
        username="user_b",
        email="b@test.com",
        first_name="B",
        last_name="User",
    )

    publisher = Publisher.objects.create(name="Test Publisher")
    author = BookAuthor.objects.create(name="Test Author")

    book_a1 = make_copy(
        "Book A1",
        owner=user_a,
        publisher=publisher,
        author=author,
        is_for_barter=True,
        trade_status="available",
    )
    book_a2 = make_copy(
        "Book A2",
        owner=user_a,
        publisher=publisher,
        author=author,
        is_for_barter=True,
        trade_status="available",
    )
    book_b1 = make_copy(
        "Book B1",
        owner=user_b,
        publisher=publisher,
        author=author,
        is_for_barter=True,
        trade_status="available",
    )
    book_b2 = make_copy(
        "Book B2",
        owner=user_b,
        publisher=publisher,
        author=author,
        is_for_barter=False,
        trade_status="available",
    )

    return {
        "user_a": user_a,
        "user_b": user_b,
        "book_a1": book_a1,
        "book_a2": book_a2,
        "book_b1": book_b1,
        "book_b2": book_b2,
    }


@pytest.mark.django_db
def test_successful_barter_flow(setup_users_and_books):
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]

    client.force_authenticate(user_a)
    create_res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b1.id),
        },
        format="json",
    )
    assert create_res.status_code == 201
    barter_id = create_res.data["barter"]["id"]
    offered_ids = create_res.data["barter"]["offered_book_ids"]
    assert offered_ids

    # recipient accepts one of the offered books
    client.force_authenticate(user_b)
    accept_res = client.post(
        reverse(
            "barter:accept-book",
            kwargs={"request_id": barter_id, "book_id": offered_ids[0]},
        )
    )
    assert accept_res.status_code == 200

    barter = BarterRequest.objects.get(pk=barter_id)
    assert barter.status == "completed"
    assert str(barter.offered_book_id) == str(offered_ids[0])

    # ownership swapped and trade statuses updated
    barter.offered_book.refresh_from_db()
    barter.requested_book.refresh_from_db()
    assert barter.offered_book.owner == user_b
    assert barter.requested_book.owner == user_a
    assert barter.offered_book.trade_status == "traded"
    assert barter.requested_book.trade_status == "traded"
    assert barter.offered_book.is_for_barter is False
    assert barter.requested_book.is_for_barter is False

    # notifications generated for both sides
    assert Notification.objects.filter(
        recipient=user_b, notification_type="barter_completed"
    ).exists()
    assert Notification.objects.filter(
        recipient=user_a, notification_type="barter_accepted"
    ).exists()


@pytest.mark.django_db
def test_recipient_can_reject(setup_users_and_books):
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]

    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b1.id),
        },
        format="json",
    )
    barter_id = res.data["barter"]["id"]

    client.force_authenticate(user_b)
    reject_res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        {"response_message": "No thanks"},
        format="json",
    )
    assert reject_res.status_code == 200
    barter = BarterRequest.objects.get(pk=barter_id)
    assert barter.status == "rejected"
    book_b1.refresh_from_db()
    assert book_b1.trade_status == "available"


@pytest.mark.django_db
def test_only_recipient_can_accept(setup_users_and_books):
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]

    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b1.id),
        },
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    offered_ids = res.data["barter"]["offered_book_ids"]

    # requester (A) tries to accept → forbidden
    client.force_authenticate(user_a)
    accept_res = client.post(
        reverse(
            "barter:accept-book",
            kwargs={"request_id": barter_id, "book_id": offered_ids[0]},
        )
    )
    assert accept_res.status_code == 403


@pytest.mark.django_db
def test_cannot_request_unavailable_or_not_for_barter(setup_users_and_books):
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b2 = data["book_b2"]  # not for barter

    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b2.id),
        },
        format="json",
    )
    assert res.status_code == 400

    # lock book and try again
    book_b2.trade_status = "not_available"
    book_b2.is_for_barter = True
    book_b2.save()
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b2.id),
        },
        format="json",
    )
    assert res.status_code == 400
