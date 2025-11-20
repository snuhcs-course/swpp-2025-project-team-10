"""
Views for the barter app.
"""

from accounts.serializers import UserBarterInfoSerializer
from barter.models import BarterRequest
from barter.serializers import (
    BarterCreateSerializer,
    BarterRejectSerializer,
    BarterRequestSerializer,
)
from books.models import BookCopy
from books.serializers import BookSummarySerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from notify.models import Notification
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_barter_request_detail(request, request_id):
    """
    Get barter request detail for approval screen.
    Returns requester info and the proposed books/messages.
    """
    try:
        barter_request = BarterRequest.objects.select_related(
            "requester",
            "recipient",
            "requested_book__publication",
            "offered_book__publication",
        ).get(pk=request_id)
    except BarterRequest.DoesNotExist:
        return Response(
            {"error": "Barter request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.user.id not in [
        barter_request.requester_id,
        barter_request.recipient_id,
    ]:
        return Response(
            {"error": "You don't have permission to view this request"},
            status=status.HTTP_403_FORBIDDEN,
        )

    offered_books = (
        BookCopy.objects.filter(id__in=barter_request.offered_book_ids)
        .select_related("publication", "owner")
        .prefetch_related("publication__authors", "publication__genres")
    )
    books_data = BookSummarySerializer(offered_books, many=True).data

    messages = (
        barter_request.message.split("\n---\n")
        if barter_request.message
        else []
    )

    requester_serializer = UserBarterInfoSerializer(
        barter_request.requester, context={"request": request}
    )

    return Response(
        {
            "id": str(barter_request.id),
            "requesterName": barter_request.requester.username,
            "requesterAvatarUrl": requester_serializer.data.get(
                "profile_picture"
            ),
            "createdAt": barter_request.created_at.isoformat(),
            "books": books_data,
            "message": messages,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_barter_request(request):
    """
    Create a new barter request.
    Requester (A) selects recipient's (B) book.
    Backend automatically selects up to 3 of A's available books and generates default messages.
    """
    serializer = BarterCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    recipient_id = request.data.get("recipient_id")
    requested_book_id = serializer.validated_data["requested_book_id"]

    if not recipient_id:
        return Response(
            {"error": "recipient_id is required"},
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
        requested_book = BookCopy.objects.select_related(
            "owner", "publication"
        ).get(pk=requested_book_id)
    except BookCopy.DoesNotExist:
        return Response(
            {"error": "Requested book not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if requested_book.owner_id != recipient_id:
        return Response(
            {"error": "Requested book must belong to recipient"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requested_book.owner_id == request.user.id:
        return Response(
            {"error": "Cannot request your own book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if (
        not requested_book.is_for_barter
        or requested_book.trade_status != "available"
    ):
        return Response(
            {"error": "Requested book is not available for barter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offered_books = list(
        BookCopy.objects.filter(
            owner=request.user,
            is_for_barter=True,
            trade_status="available",
        )
        .select_related("publication")
        .order_by("?")[:3]
    )

    message_templates = [
        "I'd like to offer '{}' for exchange.",
        "Would you be interested in '{}'?",
        "This is '{}' from my collection.",
    ]
    messages = []
    for idx, book in enumerate(offered_books):
        template = message_templates[idx % len(message_templates)]
        messages.append(template.format(book.title))

    requested_book.trade_status = "not_available"
    requested_book.save(update_fields=["trade_status"])

    if offered_books:
        BookCopy.objects.filter(id__in=[b.id for b in offered_books]).update(
            trade_status="not_available"
        )

    barter = BarterRequest.objects.create(
        requester=request.user,
        recipient=recipient,
        requested_book=requested_book,
        offered_book_ids=(
            [str(b.id) for b in offered_books] if offered_books else []
        ),
        message="\n---\n".join(messages) if messages else "",
        status="pending",
    )

    Notification.objects.create(
        recipient=recipient,
        sender=request.user,
        notification_type="barter_request",
        title="New barter request",
        message=f"{request.user.username} wants to trade for '{requested_book.title}'.",
        content_object=barter,
    )

    result_serializer = BarterRequestSerializer(
        barter, context={"request": request}
    )
    return Response(
        {"barter": result_serializer.data}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def accept_book_for_counter_propose(request, request_id, book_id):
    """
    Recipient (B) accepts one of the proposed books to complete the barter transaction.
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

    if request.user.id != barter_request.recipient_id:
        return Response(
            {"error": "Only the recipient can accept a book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if barter_request.status != "pending":
        return Response(
            {"error": f"Request is already {barter_request.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    book_id_str = str(book_id)
    if book_id_str not in barter_request.offered_book_ids:
        return Response(
            {"error": "Selected book is not in the proposed books"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    selected_book = (
        BookCopy.objects.select_related("owner", "publication")
        .filter(pk=book_id)
        .first()
    )
    if not selected_book:
        return Response(
            {"error": "Selected book not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if selected_book.owner_id != barter_request.requester_id:
        return Response(
            {"error": "Selected book is no longer owned by the requester"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    requested_book = barter_request.requested_book
    if not requested_book:
        return Response(
            {"error": "Requested book is missing from this barter request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if selected_book.trade_status == "traded":
        return Response(
            {"error": "Selected book is no longer available"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requested_book.trade_status == "traded":
        return Response(
            {"error": "Your book is no longer available for barter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        original_requester = barter_request.requester
        original_recipient = barter_request.recipient

        selected_book.owner = original_recipient
        selected_book.is_for_barter = False
        selected_book.trade_status = "traded"
        selected_book.save(
            update_fields=["owner", "is_for_barter", "trade_status"]
        )

        requested_book.owner = original_requester
        requested_book.is_for_barter = False
        requested_book.trade_status = "traded"
        requested_book.save(
            update_fields=["owner", "is_for_barter", "trade_status"]
        )

        non_selected_book_ids = [
            bid
            for bid in barter_request.offered_book_ids
            if bid != book_id_str
        ]
        BookCopy.objects.filter(id__in=non_selected_book_ids).update(
            trade_status="available"
        )

        barter_request.offered_book = selected_book
        barter_request.status = "completed"
        barter_request.completed_date = timezone.now()
        barter_request.save(
            update_fields=["offered_book", "status", "completed_date"]
        )

        Notification.objects.create(
            recipient=original_requester,
            sender=request.user,
            notification_type="barter_accepted",
            title="Barter accepted",
            message=f"{original_recipient.username} accepted your barter proposal.",
            content_object=barter_request,
        )

        Notification.objects.create(
            recipient=original_recipient,
            sender=original_requester,
            notification_type="barter_completed",
            title="Barter completed",
            message=f"Barter with {original_requester.username} completed.",
            content_object=barter_request,
        )

    return Response(
        {"message": "Barter accepted and completed successfully"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def accept_barter_request(request, request_id):
    """
    Legacy acceptance endpoint without specifying offered book.
    Marks request as accepted and notifies requester.
    """
    try:
        barter_request = BarterRequest.objects.select_related(
            "requester", "recipient"
        ).get(pk=request_id)
    except BarterRequest.DoesNotExist:
        return Response(
            {"error": "Barter request not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if barter_request.recipient_id != request.user.id:
        return Response(
            {"error": "Only the recipient can accept this request"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if barter_request.status in ["accepted", "completed"]:
        return Response(
            {"error": "Request already completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    barter_request.status = "accepted"
    barter_request.response_message = request.data.get("response_message", "")
    barter_request.response_date = timezone.now()
    barter_request.save(
        update_fields=["status", "response_message", "response_date"]
    )

    Notification.objects.create(
        recipient=barter_request.requester,
        sender=request.user,
        notification_type="barter_accepted",
        title="Barter accepted",
        message=f"{request.user.username} accepted your barter request.",
        content_object=barter_request,
    )

    serializer = BarterRequestSerializer(
        barter_request, context={"request": request}
    )
    return Response({"barter": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reject_barter_request(request, request_id):
    """
    Reject a barter request (can be done by recipient or requester).
    Restores availability of all books (1 requested + proposed offers) to 'available'.
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

    if (
        barter_request.recipient_id != request.user.id
        and barter_request.requester_id != request.user.id
    ):
        return Response(
            {
                "error": "Only the requester or recipient can reject this request"
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if barter_request.status in ["completed", "rejected", "accepted"]:
        return Response(
            {"error": f"Request already {barter_request.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = BarterRejectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        if barter_request.requested_book:
            barter_request.requested_book.trade_status = "available"
            barter_request.requested_book.save(update_fields=["trade_status"])

        BookCopy.objects.filter(id__in=barter_request.offered_book_ids).update(
            trade_status="available"
        )

        barter_request.status = "rejected"
        barter_request.response_message = serializer.validated_data.get(
            "response_message", ""
        )
        barter_request.response_date = timezone.now()
        barter_request.save(
            update_fields=[
                "status",
                "response_message",
                "response_date",
            ]
        )

        other_user = (
            barter_request.requester
            if request.user.id == barter_request.recipient_id
            else barter_request.recipient
        )
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
    return Response(
        {"barter": result_serializer.data}, status=status.HTTP_200_OK
    )
