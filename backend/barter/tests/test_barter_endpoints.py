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


@pytest.mark.django_db
def test_barter_create_accept_reject_flow():
    client = APIClient()
    requester = User.objects.create(
        username="req", email="r@example.com", first_name="R", last_name="Q"
    )
    recipient = User.objects.create(
        username="rec", email="c@example.com", first_name="C", last_name="P"
    )

    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    publication = BookPublication.objects.create(
        title="TradeMe",
        publisher=publisher,
    )
    publication.authors.add(auth)
    book = BookCopy.objects.create(
        publication=publication,
        owner=recipient,
    )

    # Create
    client.force_authenticate(requester)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": recipient.id,
            "requested_book_id": str(book.id),
        },
        format="json",
    )
    assert res.status_code == 201
    barter_id = res.data["barter"]["id"]
    assert Notification.objects.filter(
        recipient=recipient, notification_type="barter_request"
    ).exists()

    # Accept (as recipient)
    client.force_authenticate(recipient)
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": barter_id}),
        {"response_message": "ok"},
        format="json",
    )
    assert res.status_code == 200
    assert BarterRequest.objects.get(pk=barter_id).status == "accepted"
    assert Notification.objects.filter(
        recipient=requester, notification_type="barter_accepted"
    ).exists()

    # Reject should fail now (already accepted)
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        {"response_message": "no"},
        format="json",
    )
    assert res.status_code == 400
