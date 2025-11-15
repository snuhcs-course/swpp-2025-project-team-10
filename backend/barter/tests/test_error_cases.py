"""
Test error cases for barter app views to improve coverage.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Author as BookAuthor, Book, Publisher
from barter.models import BarterRequest


User = get_user_model()


@pytest.mark.django_db
def test_create_request_missing_fields():
    """Test create barter request with missing required fields."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Missing recipient_id
    res = client.post(
        reverse("barter:create-request"),
        {"requested_book_id": "123"},
        format="json",
    )
    assert res.status_code == 400
    assert "required" in res.data["error"].lower()
    
    # Missing requested_book_id
    res = client.post(
        reverse("barter:create-request"),
        {"recipient_id": 1},
        format="json",
    )
    assert res.status_code == 400
    assert "required" in res.data["error"].lower()


@pytest.mark.django_db
def test_create_request_recipient_not_found():
    """Test create barter request with nonexistent recipient."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": 99999,
            "requested_book_id": "00000000-0000-0000-0000-000000000000",
        },
        format="json",
    )
    assert res.status_code == 404
    assert "recipient" in res.data["error"].lower()


@pytest.mark.django_db
def test_create_request_book_not_found():
    """Test create barter request with nonexistent book."""
    client = APIClient()
    user_a = User.objects.create(username="a", email="a@test.com", first_name="A", last_name="User")
    user_b = User.objects.create(username="b", email="b@test.com", first_name="B", last_name="User")
    client.force_authenticate(user_a)
    
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": "00000000-0000-0000-0000-000000000000",
        },
        format="json",
    )
    assert res.status_code == 404
    assert "book not found" in res.data["error"].lower()


@pytest.mark.django_db
def test_create_request_book_not_owned_by_recipient():
    """Test create barter request where book doesn't belong to recipient."""
    client = APIClient()
    user_a = User.objects.create(username="a", email="a@test.com", first_name="A", last_name="User")
    user_b = User.objects.create(username="b", email="b@test.com", first_name="B", last_name="User")
    user_c = User.objects.create(username="c", email="c@test.com", first_name="C", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(
        title="Book",
        owner=user_c,  # Owned by C, not B
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book.id),
        },
        format="json",
    )
    assert res.status_code == 400
    assert "belong to recipient" in res.data["error"].lower()


@pytest.mark.django_db
def test_create_request_own_book():
    """Test cannot request own book."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    
    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(
        title="MyBook",
        owner=user,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    client.force_authenticate(user)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user.id,
            "requested_book_id": str(book.id),
        },
        format="json",
    )
    assert res.status_code == 403
    assert "own book" in res.data["error"].lower()


@pytest.mark.django_db
def test_counter_propose_nonexistent_request():
    """Test counter-propose with invalid request_id."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Use a valid UUID format
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": fake_uuid}),
        {"offered_book_id": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_accept_nonexistent_request():
    """Test accept with invalid request_id."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Use a valid UUID format
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": fake_uuid}),
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_reject_nonexistent_request():
    """Test reject with invalid request_id."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Use a valid UUID format
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": fake_uuid}),
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_counter_propose_missing_offered_book():
    """Test counter-propose without offered_book_id."""
    client = APIClient()
    user_a = User.objects.create(username="a", email="a@test.com", first_name="A", last_name="User")
    user_b = User.objects.create(username="b", email="b@test.com", first_name="B", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(
        title="Book",
        owner=user_b,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    # Create request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book.id),
        },
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # Counter-propose without offered_book_id
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {},
        format="json",
    )
    assert res.status_code == 400
    assert "required" in res.data["error"].lower()


@pytest.mark.django_db
def test_counter_propose_nonexistent_book():
    """Test counter-propose with nonexistent offered_book_id."""
    client = APIClient()
    user_a = User.objects.create(username="a", email="a@test.com", first_name="A", last_name="User")
    user_b = User.objects.create(username="b", email="b@test.com", first_name="B", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book = Book.objects.create(
        title="Book",
        owner=user_b,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book.authors.add(auth)
    
    # Create request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book.id),
        },
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # Counter-propose with invalid book
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )
    assert res.status_code == 404
    assert "book not found" in res.data["error"].lower()


@pytest.mark.django_db
def test_counter_propose_not_requester_book():
    """Test counter-propose with book not owned by original requester."""
    client = APIClient()
    user_a = User.objects.create(username="a", email="a@test.com", first_name="A", last_name="User")
    user_b = User.objects.create(username="b", email="b@test.com", first_name="B", last_name="User")
    user_c = User.objects.create(username="c", email="c@test.com", first_name="C", last_name="User")
    
    publisher = Publisher.objects.create(name="Pub")
    auth = BookAuthor.objects.create(name="Auth")
    book_b = Book.objects.create(
        title="BookB",
        owner=user_b,
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book_b.authors.add(auth)
    
    book_c = Book.objects.create(
        title="BookC",
        owner=user_c,  # Owned by C, not A
        publisher=publisher,
        is_for_barter=True,
        trade_status="available"
    )
    book_c.authors.add(auth)
    
    # A creates request
    client.force_authenticate(user_a)
    res = client.post(
        reverse("barter:create-request"),
        {
            "recipient_id": user_b.id,
            "requested_book_id": str(book_b.id),
        },
        format="json",
    )
    barter_id = res.data["barter"]["id"]
    
    # B tries to counter-propose with C's book
    client.force_authenticate(user_b)
    res = client.post(
        reverse("barter:counter-propose", kwargs={"request_id": barter_id}),
        {"offered_book_id": str(book_c.id)},
        format="json",
    )
    assert res.status_code == 400
    assert "belong to" in res.data["error"].lower()


@pytest.mark.django_db
def test_accept_nonexistent_request():
    """Test accept with invalid request_id."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Use a valid UUID format
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    res = client.post(
        reverse("barter:accept-request", kwargs={"request_id": fake_uuid}),
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_reject_nonexistent_request():
    """Test reject with invalid request_id."""
    client = APIClient()
    user = User.objects.create(username="user", email="u@test.com", first_name="U", last_name="ser")
    client.force_authenticate(user)
    
    # Use a valid UUID format
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    res = client.post(
        reverse("barter:reject-request", kwargs={"request_id": fake_uuid}),
        format="json",
    )
    assert res.status_code == 404
