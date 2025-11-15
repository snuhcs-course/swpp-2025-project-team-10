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
    BookSummarySerializer,
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


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_books_list(request):
    """
    Get list of books owned by the current user.
    
    GET /library/books/
    
    Returns list of books with id, title, author, coverUrl
    """
    books = Book.objects.filter(owner=request.user).select_related("publisher").prefetch_related("authors")
    
    # Map to frontend's expected Book format
    results = []
    for book in books:
        results.append({
            "id": str(book.id),
            "title": book.title,
            "author": book.author_names if hasattr(book, 'author_names') else ", ".join([a.name for a in book.authors.all()]),
            "coverUrl": request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
        })
    
    return Response(results, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_wishlist_list(request):
    """
    Get list of books in the current user's wishlist.
    
    GET /library/wishlist/
    
    Returns list of books with id, title, author, coverUrl
    """
    wishlist_items = BookWishlist.objects.filter(user=request.user).select_related("book__publisher").prefetch_related("book__authors")
    
    # Map to frontend's expected Book format
    results = []
    for item in wishlist_items:
        book = item.book
        results.append({
            "id": str(book.id),
            "title": book.title,
            "author": book.author_names if hasattr(book, 'author_names') else ", ".join([a.name for a in book.authors.all()]),
            "coverUrl": request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
        })
    
    return Response(results, status=status.HTTP_200_OK)


@api_view(["POST", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, book_id):
    """
    Add or remove a book from user's wishlist.
    
    POST /library/books/{book_id}/wishlist/ - Add to wishlist
    DELETE /library/books/{book_id}/wishlist/ - Remove from wishlist
    
    Returns status 200 on success
    """
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "POST":
        # Add to wishlist
        wishlist_item, created = BookWishlist.objects.get_or_create(
            user=request.user,
            book=book
        )
        if created:
            # Notify the book owner when their book is wishlisted
            if getattr(book, "owner", None):
                Notification.objects.create(
                    recipient=book.owner,
                    sender=request.user,
                    notification_type="book_wishlisted",
                    title=f"{request.user.username} wishlisted your book",
                    message=f"{request.user.username} added '{book.title}' to their wishlist",
                )
        return Response({"message": "Added to wishlist"}, status=status.HTTP_200_OK)
    
    elif request.method == "DELETE":
        # Remove from wishlist
        deleted_count, _ = BookWishlist.objects.filter(
            user=request.user,
            book=book
        ).delete()
        if deleted_count > 0:
            return Response({"message": "Removed from wishlist"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Not in wishlist"}, status=status.HTTP_200_OK)


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
