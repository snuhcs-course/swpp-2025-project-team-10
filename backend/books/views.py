"""
Views for the books app.
Handles book review API endpoints.
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Book, BookReview, BookWishlist, ReviewHelpfulVote, BookCollection, ReadingStatus
from django.shortcuts import get_object_or_404
from notify.models import Notification
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    BookSummarySerializer,
    CreateReviewSerializer,
    ReviewLikeResponseSerializer,
    ReviewSerializer, BookReview, BookSerializer, BookCollectionSerializer, ReadingStatusSerializer
)
from accounts.serializers import UserSerializer

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
            if request.user != review.reviewer:
                create_notification(request,type_of_notification='review_like',review_id=review.id)


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
def user_profile_detail(request, user_id: int):
    """
    Get public profile of a specific user by ID.
    Returns same structure as UserProfileMeView for consistency.

    GET /library/profile/{user_id}/
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Build frontend-compatible profile (same as UserProfileMeView)
    profile_url = None
    if user.profile_picture:
        profile_url = request.build_absolute_uri(user.profile_picture.url)

    # Taste and preferences
    favorite_genres = []
    trade_location1 = None
    trade_spot1 = None
    try:
        taste = user.taste
        favorite_genres = taste.favorite_genres or []
        trade_location1 = taste.trade_place_name or None
        trade_spot1 = taste.trade_address or None
    except Exception:
        pass

    # Compute counts
    review_count = BookReview.objects.filter(reviewer=user).count()
    follower_count = user.follower_relationships.count()
    following_count = user.following_relationships.count()

    return Response({
        "username": user.username,
        "bio": user.bio,
        "profileUrl": profile_url,
        "reviewCount": review_count,
        "followerCount": follower_count,
        "followingCount": following_count,
        "favoriteGenres": favorite_genres,
        "preferences": {
            "tradeLocation1": trade_location1,
            "tradeLocation2": None,
            "tradeSpot1": trade_spot1,
            "tradeSpot2": None,
            "favBook": None,
            "favBookNote": None,
            "favAuthor": None,
            "favAuthorNote": None,
            "readingHabit": None,
        },
    }, status=status.HTTP_200_OK)


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
def user_books_list_by_id(request, user_id: int):
    """
    Get list of books owned by a specific user.

    GET /library/books/{user_id}/
    """
    try:
        owner = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    books = (
        Book.objects.filter(owner=owner)
        .select_related("publisher")
        .prefetch_related("authors")
    )

    results = []
    for book in books:
        results.append(
            {
                "id": str(book.id),
                "title": book.title,
                "author": book.author_names if hasattr(book, "author_names") else ", ".join([a.name for a in book.authors.all()]),
                "coverUrl": request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
            }
        )

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


@api_view(["GET"]) 
@permission_classes([permissions.IsAuthenticated])
def user_wishlist_by_id(request, user_id: int):
    """
    Get list of books in a specific user's wishlist.

    GET /library/wishlist/{user_id}/
    """
    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    wishlist_items = (
        BookWishlist.objects.filter(user=target_user)
        .select_related("book__publisher")
        .prefetch_related("book__authors")
    )

    results = []
    for item in wishlist_items:
        book = item.book
        results.append(
            {
                "id": str(book.id),
                "title": book.title,
                "author": book.author_names if hasattr(book, "author_names") else ", ".join([a.name for a in book.authors.all()]),
                "coverUrl": request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
            }
        )

    return Response(results, status=status.HTTP_200_OK)


@api_view(["GET"]) 
@permission_classes([permissions.IsAuthenticated])
def user_reviews_by_id(request, user_id: int):
    """
    Get reviews written by a specific user.

    GET /library/reviews/{user_id}/
    """
    try:
        reviewer = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    queryset = (
        BookReview.objects.filter(reviewer=reviewer)
        .select_related("reviewer")
        .prefetch_related("helpful_votes")
    )

    serializer = ReviewSerializer(queryset, many=True, context={"request": request})
    # Return plain list to match frontend ProfileApi expectations
    return Response(serializer.data, status=status.HTTP_200_OK)


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


#GET BOOK
#UPDATE BOOK
#DELETE BOOK
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def book_detail(request, pk):
    """
    GET /books/<pk>/    - Retrieve a single book
    PUT /books/<pk>/    - Update book details (authenticated users only)
    DELETE /books/<pk>/ - Delete a book (authenticated users only)
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == "GET":
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data.copy()
        data.pop("owner", None)  # Ignore owner field if sent
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_list(request):
    """
    GET /books/  - List all books
    POST /books/ - Add a new book (owned by the authenticated user)
    """
    # print("book_list reached with method:", request.method)
    
    if request.method == "GET":
        books = Book.objects.filter(owner=request.user).select_related("publisher").prefetch_related("authors")
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save(owner=request.user)
            
            # Re-serialize the saved book with authors prefetched
            saved_book = Book.objects.prefetch_related('authors').get(pk=book.pk)
            response_serializer = BookSerializer(saved_book)
            
            # print("Check if book added: ", response_serializer.data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        # print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# --- Create & List collections ---
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def collection_list_view(request):
    user = request.user

    if request.method == "GET":
        collections = BookCollection.objects.filter(owner=user)
        serializer = BookCollectionSerializer(collections, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        name = request.data.get("name")
        if not name:
            return Response({"error": "Collection name is required."}, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get("description", "")
        is_public = request.data.get("is_public", True)

        collection = BookCollection.objects.create(
            name=name,
            description=description,
            is_public=is_public,
            owner=user
        )
        serializer = BookCollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# --- Add/Remove book from a collection ---
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def modify_collection_books(request, pk):
    user = request.user

    try:
        collection = BookCollection.objects.get(id=pk, owner=user)
    except BookCollection.DoesNotExist:
        return Response({"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND)

    book_id = request.data.get("id")
    if not book_id:
        return Response({"error": "book_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        collection.books.add(book)
        return Response({"message": f"{book.title} added to {collection.name}."})

    elif request.method == "DELETE":
        collection.books.remove(book)
        return Response({"message": f"{book.title} removed from {collection.name}."})

# --- Create & List reading status ---

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def reading_status_view(request):

    user = request.user
    # --- GET: list all reading statuses for the user ---
    if request.method == "GET":
        statuses = ReadingStatus.objects.filter(user=user)
        serializer = ReadingStatusSerializer(statuses, many=True)
        return Response(serializer.data)

    # --- POST: create or update status for a book ---
    elif request.method == "POST":
        book_id = request.data.get("id")
        if not book_id:
            return Response({"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        reading_status, created = ReadingStatus.objects.get_or_create(user=user, book=book)
        serializer = ReadingStatusSerializer(reading_status, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def modify_reading_status(request, pk):
    user = request.user
    # --- PATCH: partial update (e.g., update pages_read or status) ---
    if request.method == "PATCH":
        # Get ID from URL path (pk) instead of request.data
        try:
            reading_status = ReadingStatus.objects.get(id=pk, user=user)
        except ReadingStatus.DoesNotExist:
            return Response({"error": "Reading status not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReadingStatusSerializer(reading_status, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE: remove a reading status entry ---
    elif request.method == "DELETE":
        # Get ID from URL path (pk)
        try:
            ReadingStatus.objects.filter(id=pk, user=user).delete()
        except ReadingStatus.DoesNotExist:
            return Response({"error": "Reading status not found."},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Reading status removed."},
                        status=status.HTTP_204_NO_CONTENT)