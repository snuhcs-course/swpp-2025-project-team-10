"""
Views for the books app.
Handles book review API endpoints.
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, BookReview, BookWishlist, ReviewHelpfulVote
from notify.models import Notification
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    CreateReviewSerializer,
    ReviewLikeResponseSerializer,
    ReviewSerializer,
)

User = get_user_model()


class UserReviewListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating user's book reviews.

    GET /library/reviews/ - List all reviews by the authenticated user
    POST /library/reviews/ - Create a new review
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == "POST":
            return CreateReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        """Return only the authenticated user's reviews."""
        return (
            BookReview.objects.filter(reviewer=self.request.user)
            .select_related("reviewer")
            .prefetch_related("helpful_votes")
        )

    @extend_schema(
        summary="List User's Reviews",
        description="Get all book reviews created by the authenticated user",
        responses={
            200: OpenApiResponse(
                description="List of user's reviews",
                response=ReviewSerializer(many=True),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """List all reviews by the authenticated user."""
        queryset = self.get_queryset()
        serializer = ReviewSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"results": serializer.data})

    @extend_schema(
        summary="Create New Review",
        description="Create a new book review",
        request=CreateReviewSerializer,
        responses={
            201: OpenApiResponse(
                description="Review created successfully",
                response=ReviewSerializer,
            ),
            400: OpenApiResponse(description="Invalid data"),
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new book review."""
        serializer = CreateReviewSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                serializer.to_representation(review),
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewLikeView(APIView):
    """
    API endpoint for liking/unliking a review.

    POST /library/reviews/{id}/like/ - Toggle like on a review
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Like/Unlike Review",
        description="Toggle like on a book review. If already liked, "
        "it will unlike. If not liked, it will like.",
        responses={
            200: OpenApiResponse(
                description="Like toggled successfully",
                response=ReviewLikeResponseSerializer,
            ),
            404: OpenApiResponse(description="Review not found"),
        },
    )
    def post(self, request, pk):
        """Toggle like on a review."""
        try:
            review = (
                BookReview.objects.select_related("reviewer")
                .prefetch_related("helpful_votes")
                .get(pk=pk)
            )
        except BookReview.DoesNotExist:
            return Response(
                {"error": "Review not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user already liked this review
        existing_like = ReviewHelpfulVote.objects.filter(
            review=review, user=request.user
        ).first()

        if existing_like:
            # Unlike: remove the like
            existing_like.delete()
        else:
            # Like: add a new like
            ReviewHelpfulVote.objects.create(review=review, user=request.user)

        # Refresh the review to get updated helpful_votes
        review.refresh_from_db()
        review = (
            BookReview.objects.select_related("reviewer")
            .prefetch_related("helpful_votes")
            .get(pk=pk)
        )

        # Return updated review data
        serializer = ReviewSerializer(review, context={"request": request})
        return Response({"review": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, book_id):
    """
    Toggle the current user's wishlist for a given book (bookmark button).

    POST /books/{book_id}/wishlist/

    Returns { "wishlisted": true|false }
    """
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    existing = BookWishlist.objects.filter(user=request.user, book=book).first()
    if existing:
        existing.delete()
        wishlisted = False
    else:
        BookWishlist.objects.create(user=request.user, book=book)
        wishlisted = True
        # Record a notification for the actor (accumulates in notifications tab)
        Notification.objects.create(
            recipient=request.user,
            sender=request.user,
            notification_type="book_wishlisted",
            title="Book added to wishlist",
            message=f"You added '{book.title}' to your wishlist.",
            content_object=book,
        )

    return Response({"wishlisted": wishlisted}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def toggle_book_for_barter(request, book_id):
    """
    Toggle whether this book is available for bartering.
    Only the owner can toggle.

    PATCH /books/{book_id}/toggle-barter/

    Returns { "is_for_barter": true|false }
    """
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    # Only owner can toggle
    if book.owner_id != request.user.id:
        return Response(
            {"error": "Only the owner can toggle barter availability"},
            status=status.HTTP_403_FORBIDDEN,
        )

    book.is_for_barter = not book.is_for_barter
    book.save(update_fields=["is_for_barter"])

    return Response({"is_for_barter": book.is_for_barter}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def nearby_owners(request, book_id):
    """
    Get list of users who own this book, are willing to barter,
    and are within a given radius (default 20 km).

    GET /books/{book_id}/nearby-owners/?radius=20

    Returns list of users with distance and barter-relevant info.
    """
    from math import radians, cos, sin, asin, sqrt
    from accounts.serializers import UserBarterInfoSerializer

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    radius_km = float(request.query_params.get("radius", 20))

    # Get requester's location
    if not request.user.latitude or not request.user.longitude:
        return Response(
            {"error": "Your location is not set. Please update your profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_lat = float(request.user.latitude)
    user_lon = float(request.user.longitude)

    # Find all owners of this book who have is_for_barter=True
    # and are not the requester
    potential_owners = (
        Book.objects.filter(
            title=book.title,  # Match by title (or you can use ISBN for exact match)
            is_for_barter=True,
        )
        .exclude(owner=request.user)
        .select_related("owner")
        .prefetch_related("owner__books", "owner__wishlist")
    )

    # Calculate distance and filter
    def haversine(lon1, lat1, lon2, lat2):
        """Calculate distance in km between two lat/lon points."""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km

    results = []
    for book_instance in potential_owners:
        owner = book_instance.owner
        if not owner.latitude or not owner.longitude:
            continue
        distance = haversine(
            user_lon, user_lat, float(owner.longitude), float(owner.latitude)
        )
        if distance <= radius_km:
            owner_data = UserBarterInfoSerializer(
                owner, context={"request": request}
            ).data
            owner_data["distance_km"] = round(distance, 2)
            results.append(owner_data)

    # Sort by distance
    results.sort(key=lambda x: x["distance_km"])

    return Response({"owners": results}, status=status.HTTP_200_OK)
