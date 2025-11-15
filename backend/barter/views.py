"""
Views for the barter app.
"""

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from barter.models import BarterRequest
from barter.serializers import (
    BarterAcceptSerializer,
    BarterRejectSerializer,
    BarterRequestSerializer,
)
from books.models import Book
from notify.models import Notification

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_barter_request(request):
    """
    Create initial barter request (Step 1: A → B).
    A requests B's book without specifying which book to offer yet.
    
    POST /barter/requests/create/
    Body:
      - recipient_id: int (user ID)
      - requested_book_id: uuid (book ID from recipient)
      - message: str (optional)
    """
    recipient_id = request.data.get("recipient_id")
    requested_book_id = request.data.get("requested_book_id")

    if not recipient_id or not requested_book_id:
        return Response(
            {"error": "recipient_id and requested_book_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        recipient = User.objects.get(pk=recipient_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Recipient user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        requested_book = Book.objects.get(pk=requested_book_id)
    except Book.DoesNotExist:
        return Response(
            {"error": "Requested book not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if requested_book.owner_id != recipient_id:
        return Response(
            {"error": "Requested book must belong to recipient"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if owner allows barter for this book
    if not requested_book.is_for_barter:
        return Response(
            {"error": "This book is not available for barter (owner disabled trading)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if book is available for barter (not in pending trade)
    if requested_book.trade_status != "available":
        return Response(
            {"error": "This book is not available for barter (already in a pending trade)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify requester cannot request their own book
    if requested_book.owner_id == request.user.id:
        return Response(
            {"error": "Cannot request your own book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Build message with requester's info
    msg = request.data.get("message")
    if not msg:
        requester = request.user
        parts = [
            f"Hi {recipient.username}, I'd like to barter for your '{requested_book.title}'."
        ]
        if requester.location:
            parts.append(f"My location: {requester.location}")
        msg = "\n".join(parts)

    # Create initial barter request (no offered_book yet)
    # Mark requested_book as not_available while barter is pending
    requested_book.trade_status = "not_available"
    requested_book.save(update_fields=["trade_status"])

    barter = BarterRequest.objects.create(
        requester=request.user,
        recipient=recipient,
        offered_book=None,  # Will be set later by recipient in counter-proposal
        requested_book=requested_book,
        message=msg,
        preferred_meeting_type=request.data.get("preferred_meeting_type", "in_person"),
        proposed_meeting_location=request.data.get("proposed_meeting_location", ""),
        proposed_meeting_time=request.data.get("proposed_meeting_time"),
    )

    # Notify recipient
    Notification.objects.create(
        recipient=recipient,
        sender=request.user,
        notification_type="barter_request",
        title="New barter request",
        message=f"{request.user.username} wants to trade for '{requested_book.title}'.",
        content_object=barter,
    )

    serializer = BarterRequestSerializer(barter, context={"request": request})
    return Response({"barter": serializer.data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def counter_propose(request, request_id):
    """
    Recipient (B) selects a book from requester's (A) library to counter-propose.
    This sets the offered_book field and changes status to 'counter_proposed'.
    
    POST /barter/requests/<uuid:request_id>/counter-propose/
    Body:
      - offered_book_id: uuid (book from requester's library that B wants)
      - response_message: str (optional)
    """
    try:
        barter_request = BarterRequest.objects.select_related(
            "requester", "recipient", "requested_book"
        ).get(pk=request_id)
    except BarterRequest.DoesNotExist:
        return Response(
            {"error": "Barter request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Only recipient can counter-propose
    if barter_request.recipient_id != request.user.id:
        return Response(
            {"error": "Only the recipient can counter-propose"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if already responded or counter-proposed
    if barter_request.status not in ["pending", "counter_proposed"]:
        return Response(
            {"error": f"Cannot counter-propose: request already {barter_request.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offered_book_id = request.data.get("offered_book_id")
    if not offered_book_id:
        return Response(
            {"error": "offered_book_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offered_book = Book.objects.get(pk=offered_book_id)
    except Book.DoesNotExist:
        return Response(
            {"error": "Offered book not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verify offered book belongs to requester (A)
    if offered_book.owner_id != barter_request.requester_id:
        return Response(
            {"error": "Offered book must belong to the original requester"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if owner allows barter for this book
    if not offered_book.is_for_barter:
        return Response(
            {"error": "Selected book is not available for barter (owner disabled trading)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify offered book is available (not in pending trade)
    if offered_book.trade_status != "available":
        return Response(
            {"error": "Selected book is not available for barter (already in a pending trade)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Mark offered_book as not_available during counter-proposal
    offered_book.trade_status = "not_available"
    offered_book.save(update_fields=["trade_status"])

    # Update barter request with counter-proposal
    barter_request.offered_book = offered_book
    barter_request.status = "counter_proposed"
    barter_request.response_message = request.data.get("response_message", "")
    barter_request.response_date = timezone.now()
    barter_request.save()

    # Notify requester (A) about counter-proposal
    Notification.objects.create(
        recipient=barter_request.requester,
        sender=request.user,
        notification_type="barter_counter_proposed",
        title="Counter-proposal received",
        message=f"{request.user.username} wants to trade '{offered_book.title}' for your requested book.",
        content_object=barter_request,
    )

    result_serializer = BarterRequestSerializer(
        barter_request, context={"request": request}
    )
    return Response({"barter": result_serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def accept_barter_request(request, request_id):
    """
    Requester (A) accepts recipient's (B) counter-proposal.
    This finalizes the trade: ownership transfer + status update + availability restore.
    
    POST /barter/requests/<uuid:request_id>/accept/
    Optional body:
      - response_message: str
    """
    try:
        barter_request = BarterRequest.objects.select_related(
            "requester", "recipient", "offered_book", "requested_book"
        ).get(pk=request_id)
    except BarterRequest.DoesNotExist:
        return Response(
            {"error": "Barter request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Only requester (A) can accept counter-proposal
    if barter_request.requester_id != request.user.id:
        return Response(
            {"error": "Only the original requester can accept the counter-proposal"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if counter-proposed
    if barter_request.status != "counter_proposed":
        return Response(
            {"error": f"Cannot accept: request status is '{barter_request.status}', expected 'counter_proposed'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify both books are set
    if not barter_request.offered_book or not barter_request.requested_book:
        return Response(
            {"error": "Both offered_book and requested_book must be set to complete the trade"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Transfer ownership: offered_book (A→B), requested_book (B→A)
    offered_book = barter_request.offered_book
    requested_book = barter_request.requested_book

    # A's book → B (mark as not for barter after receiving)
    offered_book.owner = barter_request.recipient
    offered_book.trade_status = "available"
    offered_book.is_for_barter = False
    offered_book.save(update_fields=["owner", "trade_status", "is_for_barter"])

    # B's book → A (mark as not for barter after receiving)
    requested_book.owner = barter_request.requester
    requested_book.trade_status = "available"
    requested_book.is_for_barter = False
    requested_book.save(update_fields=["owner", "trade_status", "is_for_barter"])

    # Update barter request
    barter_request.status = "completed"
    barter_request.completed_date = timezone.now()
    barter_request.completion_notes = request.data.get("response_message", "Trade completed successfully")
    barter_request.save()

    # Notify recipient (B) about acceptance
    Notification.objects.create(
        recipient=barter_request.recipient,
        sender=request.user,
        notification_type="barter_completed",
        title="Trade completed!",
        message=f"{request.user.username} accepted your counter-proposal. Trade is complete!",
        content_object=barter_request,
    )

    result_serializer = BarterRequestSerializer(
        barter_request, context={"request": request}
    )
    return Response({"barter": result_serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reject_barter_request(request, request_id):
    """
    Reject a barter request (can be done by recipient or requester).
    Restores availability of involved books to 'available'.
    
    POST /barter/requests/<uuid:request_id>/reject/
    Optional body:
      - response_message: str
    """
    try:
        barter_request = BarterRequest.objects.select_related(
            "requester", "recipient", "offered_book", "requested_book"
        ).get(pk=request_id)
    except BarterRequest.DoesNotExist:
        return Response(
            {"error": "Barter request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Both requester and recipient can reject
    if barter_request.recipient_id != request.user.id and barter_request.requester_id != request.user.id:
        return Response(
            {"error": "Only the requester or recipient can reject this request"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if already finalized
    if barter_request.status in ["completed", "rejected"]:
        return Response(
            {"error": f"Request already {barter_request.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = BarterRejectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Restore book trade_status
    if barter_request.requested_book:
        barter_request.requested_book.trade_status = "available"
        barter_request.requested_book.save(update_fields=["trade_status"])

    if barter_request.offered_book:
        barter_request.offered_book.trade_status = "available"
        barter_request.offered_book.save(update_fields=["trade_status"])

    # Update barter request
    barter_request.status = "rejected"
    barter_request.response_message = serializer.validated_data.get(
        "response_message", ""
    )
    barter_request.response_date = timezone.now()
    barter_request.save()

    # Notify the other party
    other_user = barter_request.requester if request.user.id == barter_request.recipient_id else barter_request.recipient
    Notification.objects.create(
        recipient=other_user,
        sender=request.user,
        notification_type="barter_rejected",
        title="Barter request declined",
        message=f"{request.user.username} declined the barter request.",
        content_object=barter_request,
    )

    result_serializer = BarterRequestSerializer(
        barter_request, context={"request": request}
    )
    return Response({"barter": result_serializer.data}, status=status.HTTP_200_OK)
