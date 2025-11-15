"""
Test cases for the new 3-step barter exchange flow:
1. A requests B's book (pending, no offered_book)
2. B counter-proposes with a book from A's library (counter_proposed)
3. A accepts (completed, ownership transfer, is_for_barter=False)
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher
from barter.models import BarterRequest
from notify.models import Notification


User = get_user_model()


@pytest.fixture
def setup_users_and_books():
    """Create test users and books for barter scenarios."""
    # Create users
    user_a = User.objects.create(
        username="user_a", 
        email="a@test.com", 
        first_name="A", 
        last_name="User",
        phone_number="+821012345678",
        location="Seoul"
    )
    user_b = User.objects.create(
        username="user_b", 
        email="b@test.com", 
        first_name="B", 
        last_name="User",
        phone_number="+821087654321",
        location="Busan"
    )
    
    # Create publisher and author
    publisher = Publisher.objects.create(name="Test Publisher")
    author = BookAuthor.objects.create(name="Test Author")
    
    # Create books for user A
    book_a1 = Book.objects.create(
        title="Book A1",
        owner=user_a,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book_a1.authors.add(author)
    
    book_a2 = Book.objects.create(
        title="Book A2",
        owner=user_a,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book_a2.authors.add(author)
    
    # Create books for user B
    book_b1 = Book.objects.create(
        title="Book B1",
        owner=user_b,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book_b1.authors.add(author)
    
    book_b2 = Book.objects.create(
        title="Book B2",
        owner=user_b,
        publisher=publisher,
        is_for_barter=False,  # Not for barter
        trade_status="available"
    )
    book_b2.authors.add(author)
    
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
    """Test complete successful barter flow: request → counter-propose → accept."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # Step 1: A requests B's book (without specifying offered book)
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b1.id),
            "message": "I want your book!"
        },
        format="json",
    )
    assert res.status_code == 201
    barter_id = res.data["barter"]["id"]
    
    # Verify initial state
    barter = BarterRequest.objects.get(pk=barter_id)
    assert barter.status == "pending"
    assert barter.offered_book is None
    assert barter.requested_book == book_b1
    assert barter.requester == user_a
    assert barter.recipient == user_b
    
    # Verify requested book is locked
    book_b1.refresh_from_db()
    assert book_b1.trade_status == "not_available"
    
    # Verify notification sent to B
    assert Notification.objects.filter(
        recipient=user_b,
        notification_type="barter_request"
    ).exists()
    
    # Verify phone numbers are NOT exposed in pending status
    assert res.data["barter"]["requester_phone"] is None
    assert res.data["barter"]["recipient_phone"] is None
    
    # Step 2: B counter-proposes with book from A's library
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {
            "offered_book_id": str(book_a1.id),
            "response_message": "I want your Book A1 in exchange"
        },
        format="json",
    )
    assert res.status_code == 200
    
    # Verify counter-proposal state
    barter.refresh_from_db()
    assert barter.status == "counter_proposed"
    assert barter.offered_book == book_a1
    assert barter.response_message == "I want your Book A1 in exchange"
    
    # Verify offered book is now locked
    book_a1.refresh_from_db()
    assert book_a1.trade_status == "not_available"
    
    # Verify notification sent to A
    assert Notification.objects.filter(
        recipient=user_a,
        notification_type="barter_counter_proposed"
    ).exists()
    
    # Verify phone numbers still NOT exposed in counter_proposed status
    assert res.data["barter"]["requester_phone"] is None
    assert res.data["barter"]["recipient_phone"] is None
    
    # Step 3: A accepts counter-proposal
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": barter_id}),
        {"response_message": "Deal!"},
        format="json",
    )
    assert res.status_code == 200
    
    # Verify completed state
    barter.refresh_from_db()
    assert barter.status == "completed"
    assert barter.completion_notes == "Deal!"
    
    # Verify ownership transfer
    book_a1.refresh_from_db()
    book_b1.refresh_from_db()
    assert book_a1.owner == user_b  # A's book → B
    assert book_b1.owner == user_a  # B's book → A
    
    # Verify trade_status restored
    assert book_a1.trade_status == "available"
    assert book_b1.trade_status == "available"
    
    # Verify is_for_barter set to False
    assert book_a1.is_for_barter is False
    assert book_b1.is_for_barter is False
    
    # Verify notification sent to B
    assert Notification.objects.filter(
        recipient=user_b,
        notification_type="barter_completed"
    ).exists()
    
    # Verify phone numbers ARE exposed in completed status
    assert res.data["barter"]["requester_phone"] == user_a.phone_number
    assert res.data["barter"]["recipient_phone"] == user_b.phone_number


@pytest.mark.django_db
def test_reject_initial_request(setup_users_and_books):
    """Test B rejects A's initial request."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]
    
    # A creates request
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
    
    # B rejects
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        {"response_message": "Not interested"},
        format="json",
    )
    assert res.status_code == 200
    
    # Verify rejected state
    barter = BarterRequest.objects.get(pk=barter_id)
    assert barter.status == "rejected"
    
    # Verify book availability restored
    book_b1.refresh_from_db()
    assert book_b1.trade_status == "available"
    
    # Verify notification sent to A
    assert Notification.objects.filter(
        recipient=user_a,
        notification_type="barter_rejected"
    ).exists()


@pytest.mark.django_db
def test_reject_counter_proposal(setup_users_and_books):
    """Test A rejects B's counter-proposal."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # B counter-proposes
    client.force_authenticate(user_b)
    client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_a1.id)},
        format="json",
    )
    
    # A rejects counter-proposal
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        {"response_message": "Don't like your choice"},
        format="json",
    )
    assert res.status_code == 200
    
    # Verify rejected state
    barter = BarterRequest.objects.get(pk=barter_id)
    assert barter.status == "rejected"
    
    # Verify both books availability restored
    book_a1.refresh_from_db()
    book_b1.refresh_from_db()
    assert book_a1.trade_status == "available"
    assert book_b1.trade_status == "available"


@pytest.mark.django_db
def test_cannot_request_book_not_for_barter(setup_users_and_books):
    """Test A cannot request B's book that is not for barter."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b2 = data["book_b2"]  # is_for_barter=False
    
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
    assert "owner disabled trading" in res.data["error"]


@pytest.mark.django_db
def test_cannot_counter_propose_book_not_for_barter(setup_users_and_books):
    """Test B cannot counter-propose with A's book that is not for barter."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # Set book_a1 to not for barter
    book_a1.is_for_barter = False
    book_a1.save()
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # B tries to counter-propose with non-tradeable book
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_a1.id)},
        format="json",
    )
    assert res.status_code == 400
    assert "owner disabled trading" in res.data["error"]


@pytest.mark.django_db
def test_cannot_request_book_in_pending_trade(setup_users_and_books):
    """Test cannot request a book that is already in a pending trade."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]
    
    # Set book to pending trade
    book_b1.trade_status = "not_available"
    book_b1.save()
    
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    assert res.status_code == 400
    assert "already in a pending trade" in res.data["error"]


@pytest.mark.django_db
def test_only_requester_can_accept(setup_users_and_books):
    """Test only the original requester (A) can accept counter-proposal."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # B counter-proposes
    client.force_authenticate(user_b)
    client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_a1.id)},
        format="json",
    )
    
    # B tries to accept (should fail)
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": barter_id}),
        format="json",
    )
    assert res.status_code == 403


@pytest.mark.django_db
def test_only_recipient_can_counter_propose(setup_users_and_books):
    """Test only the recipient (B) can counter-propose."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # A tries to counter-propose (should fail)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_a1.id)},
        format="json",
    )
    assert res.status_code == 403


@pytest.mark.django_db
def test_cannot_accept_without_counter_proposal(setup_users_and_books):
    """Test cannot accept before counter-proposal."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # A tries to accept immediately (should fail - status is pending, not counter_proposed)
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": barter_id}),
        format="json",
    )
    assert res.status_code == 400
    assert "expected 'counter_proposed'" in res.data["error"]


@pytest.mark.django_db
def test_both_parties_can_reject(setup_users_and_books):
    """Test both requester and recipient can reject at any stage."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # Scenario 1: A rejects after creating request (changes mind)
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # A changes mind and cancels
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        {"response_message": "Changed my mind"},
        format="json",
    )
    assert res.status_code == 200
    assert BarterRequest.objects.get(pk=barter_id).status == "rejected"


@pytest.mark.django_db
def test_cannot_reject_already_completed(setup_users_and_books):
    """Test cannot reject an already completed trade."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_a1 = data["book_a1"]
    book_b1 = data["book_b1"]
    
    # Complete a trade
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    client.force_authenticate(user_b)
    client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_a1.id)},
        format="json",
    )
    
    client.force_authenticate(user_a)
    client.post(
        reverse("barter:accept-request", kwargs={"request_id": barter_id}),
        format="json",
    )
    
    # Try to reject completed trade (should fail)
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": barter_id}),
        format="json",
    )
    assert res.status_code == 400
    assert "already completed" in res.data["error"]


@pytest.mark.django_db
def test_message_includes_location(setup_users_and_books):
    """Test auto-generated message includes requester's location."""
    client = APIClient()
    data = setup_users_and_books
    user_a = data["user_a"]
    user_b = data["user_b"]
    book_b1 = data["book_b1"]
    
    # A creates request without custom message
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": user_b.id, "requested_book_id": str(book_b1.id)},
        format="json",
    )
    
    barter = BarterRequest.objects.get(pk=res.data["barter"]["id"])
    assert "Seoul" in barter.message  # user_a's location
    assert book_b1.title in barter.message
