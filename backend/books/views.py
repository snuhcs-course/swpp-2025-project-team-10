"""
Views for the books app.
Combines legacy review endpoints with the updated library/profile APIs.
"""

from math import asin, cos, radians, sin, sqrt

from accounts.serializers import UserBarterInfoSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from notify.models import Notification
from notify.utils import create_notification
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BookCollection,
    BookCopy,
    BookReview,
    BookWishlist,
    ReadingStatus,
    ReviewHelpfulVote,
)
from .serializers import (
    BookCollectionSerializer,
    BookSerializer,
    CreateReviewSerializer,
    ReadingStatusSerializer,
    ReviewLikeResponseSerializer,
    ReviewSerializer,
)
from .services.publication_categories import PublicationCategorizer

User = get_user_model()

# --- Onboarding Views ---
from .models import Author, Genre, BookPublication
from .serializers import OnboardingAuthorSerializer, OnboardingBookSerializer, OnboardingGenreSerializer
from rest_framework.permissions import AllowAny



def _build_book_card(book: BookCopy, request) -> dict:
    """Return a lightweight payload for library/wishlist endpoints."""
    cover_url = None
    if book.cover_image:
        cover_url = (
            request.build_absolute_uri(book.cover_image.url)
            if request
            else book.cover_image.url
        )
    return {
        "id": str(book.id),
        "title": book.title,
        "author": book.author_names,
        "coverUrl": cover_url,
    }


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
        description="Toggle like on a book review. If already liked, it will unlike.",
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

        existing_like = ReviewHelpfulVote.objects.filter(
            review=review, user=request.user
        ).first()

        if existing_like:
            existing_like.delete()
        else:
            ReviewHelpfulVote.objects.create(review=review, user=request.user)
            if request.user != review.reviewer:
                create_notification(
                    request,
                    type_of_notification="review_like",
                    review_id=review.id,
                )

        review.refresh_from_db()
        serializer = ReviewSerializer(review, context={"request": request})
        return Response({"review": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_profile_detail(request, user_id: int):
    """
    Get public profile of a specific user by ID.
    Returns same structure as UserProfileMeView for consistency.
    """

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    profile_url = None
    if user.profile_picture:
        profile_url = request.build_absolute_uri(user.profile_picture.url)

    favorite_genres = []
    trade_location1 = None
    trade_spot1 = None
    # Safe fallback: ensure taste is defined even if user has no taste profile
    taste = None
    try:
        taste = user.taste
        favorite_genres = taste.favorite_genres or []
        trade_location1 = taste.trade_place_name or None
        trade_spot1 = taste.trade_address or None
    except Exception:
        pass

    # UserPreferences에서 추가 필드 가져오기 (favorites from taste, notes & locations from preferences)
    trade_location2 = None
    trade_spot2 = None
    fav_books = []
    fav_book_notes = []
    fav_authors = []
    fav_author_notes = []
    reading_habit = None
    try:
        fav_books = getattr(taste, "favorite_books", []) or []
        fav_authors = getattr(taste, "favorite_authors", []) or []
    except Exception:
        # Safe fallback: if taste is None or attribute access fails
        fav_books = []
        fav_authors = []
    try:
        user_prefs = user.preferences
        import json
        if user_prefs.preferred_meeting_locations:
            try:
                meta = json.loads(user_prefs.preferred_meeting_locations)
            except Exception:
                meta = {}
            trade_location2 = meta.get("tradeLocation2")
            trade_spot2 = meta.get("tradeSpot2")
            fav_book_notes = meta.get("favBookNotes", [])
            fav_author_notes = meta.get("favAuthorNotes", [])
            reading_habit = meta.get("readingHabit")
    except Exception:
        pass

    review_count = BookReview.objects.filter(reviewer=user).count()
    follower_count = user.follower_relationships.count()
    following_count = user.following_relationships.count()

    return Response(
        {
            "username": user.username,
            "bio": user.bio,
            "profileUrl": profile_url,
            "reviewCount": review_count,
            "followerCount": follower_count,
            "followingCount": following_count,
            "favoriteGenres": favorite_genres or [],
            "preferences": {
                "tradeLocation1": trade_location1,
                "tradeLocation2": trade_location2,
                "tradeSpot1": trade_spot1,
                "tradeSpot2": trade_spot2,
                "favBooks": fav_books or [],
                "favBookNotes": fav_book_notes or [],
                "favAuthors": fav_authors or [],
                "favAuthorNotes": fav_author_notes or [],
                "readingHabit": reading_habit,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_books_list(request):
    """
    Get list of books owned by the current user.
    Returns the minimal structure expected by the Android profile screens.
    """

    books = (
        BookCopy.objects.filter(owner=request.user)
        .select_related("publication")
        .prefetch_related("publication__authors")
    )
    return Response(
        [_build_book_card(book, request) for book in books],
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_books_list_by_id(request, user_id: int):
    """Get list of books owned by a specific user."""

    try:
        owner = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    books = (
        BookCopy.objects.filter(owner=owner)
        .select_related("publication")
        .prefetch_related("publication__authors")
    )
    return Response(
        [_build_book_card(book, request) for book in books],
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_wishlist_list(request):
    """Return current user's wishlist."""

    wishlist_items = (
        BookWishlist.objects.filter(user=request.user)
        .select_related("book__publication")
        .prefetch_related("book__publication__authors")
    )
    books = [item.book for item in wishlist_items]
    return Response(
        [_build_book_card(book, request) for book in books],
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_wishlist_by_id(request, user_id: int):
    """Return wishlist for a specific user."""

    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    wishlist_items = (
        BookWishlist.objects.filter(user=target_user)
        .select_related("book__publication")
        .prefetch_related("book__publication__authors")
    )
    books = [item.book for item in wishlist_items]
    return Response(
        [_build_book_card(book, request) for book in books],
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_reviews_by_id(request, user_id: int):
    """Get reviews written by a specific user."""

    try:
        reviewer = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    queryset = (
        BookReview.objects.filter(reviewer=reviewer)
        .select_related("reviewer")
        .prefetch_related("helpful_votes")
    )
    serializer = ReviewSerializer(
        queryset, many=True, context={"request": request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, book_id):
    """
    Add or remove a book from user's wishlist.
    POST adds (idempotent), DELETE removes.
    """

    book = get_object_or_404(
        BookCopy.objects.select_related("owner", "publication"), pk=book_id
    )

    if request.method == "POST":
        wishlist_item, created = BookWishlist.objects.get_or_create(
            user=request.user,
            book=book,
        )
        if created and book.owner_id and book.owner_id != request.user.id:
            Notification.objects.create(
                recipient=book.owner,
                sender=request.user,
                notification_type="book_wishlisted",
                title=f"{request.user.username} wishlisted your book",
                message=f"{request.user.username} added '{book.title}' to their wishlist.",
                content_object=book,
            )
        return Response({"wishlisted": True}, status=status.HTTP_200_OK)

    deleted_count, _ = BookWishlist.objects.filter(
        user=request.user, book=book
    ).delete()
    if deleted_count > 0:
        data = {
            "wishlisted": False,
            "removed": True,
            "message": "Removed from wishlist",
        }
    else:
        data = {
            "wishlisted": False,
            "removed": False,
            "message": "Not in wishlist",
        }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def toggle_book_for_barter(request, book_id):
    """
    Toggle whether this book copy is available for bartering.
    Only the owner can toggle.
    """

    try:
        book = BookCopy.objects.select_related("owner").get(pk=book_id)
    except BookCopy.DoesNotExist:
        return Response(
            {"error": "Book not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if book.owner_id != request.user.id:
        return Response(
            {"error": "Only the owner can toggle barter availability"},
            status=status.HTTP_403_FORBIDDEN,
        )

    book.is_for_barter = not book.is_for_barter
    book.save(update_fields=["is_for_barter"])
    return Response(
        {"is_for_barter": book.is_for_barter}, status=status.HTTP_200_OK
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def book_detail(request, pk):
    """Retrieve, update, or delete a specific book copy."""

    book = get_object_or_404(
        BookCopy.objects.select_related("publication", "owner"), pk=pk
    )

    if request.method == "GET":
        serializer = BookSerializer(book, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = BookSerializer(
            book, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    book.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_list(request):
    """List all book copies or create a new one owned by the authenticated user."""

    if request.method == "GET":
        books = BookCopy.objects.filter(owner=request.user).select_related(
            "publication", "owner"
        )
        serializer = BookSerializer(
            books, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = BookSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Create & List collections ---
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def collection_list_view(request):
    """List or create collections for the authenticated user."""

    user = request.user
    if request.method == "GET":
        collections = BookCollection.objects.filter(owner=user)
        serializer = BookCollectionSerializer(collections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    name = request.data.get("name")
    if not name:
        return Response(
            {"error": "Collection name is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    collection = BookCollection.objects.create(
        name=name,
        description=request.data.get("description", ""),
        is_public=request.data.get("is_public", True),
        owner=user,
    )
    serializer = BookCollectionSerializer(collection)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def modify_collection_books(request, pk):
    """Add or remove a book copy from a collection."""

    user = request.user
    try:
        collection = BookCollection.objects.get(id=pk, owner=user)
    except BookCollection.DoesNotExist:
        return Response(
            {"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND
        )

    book_id = request.data.get("id")
    if not book_id:
        return Response(
            {"error": "book_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    book = get_object_or_404(BookCopy, id=book_id)

    if request.method == "POST":
        collection.books.add(book)
        return Response(
            {"message": f"{book.title} added to {collection.name}."},
            status=status.HTTP_200_OK,
        )

    collection.books.remove(book)
    return Response(
        {"message": f"{book.title} removed from {collection.name}."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def reading_status_view(request):
    """List or upsert reading status entries for the authenticated user."""

    user = request.user
    if request.method == "GET":
        statuses = ReadingStatus.objects.filter(user=user).select_related(
            "book"
        )
        serializer = ReadingStatusSerializer(statuses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    book_id = request.data.get("book_id") or request.data.get("id")
    if not book_id:
        return Response(
            {"error": "book_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    book = get_object_or_404(BookCopy, id=book_id)
    reading_status, created = ReadingStatus.objects.get_or_create(
        user=user, book=book
    )
    serializer = ReadingStatusSerializer(
        reading_status, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def modify_reading_status(request, pk):
    """Update or delete a specific reading status entry."""

    user = request.user
    if request.method == "PATCH":
        reading_status = get_object_or_404(ReadingStatus, id=pk, user=user)
        serializer = ReadingStatusSerializer(
            reading_status, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    deleted, _ = ReadingStatus.objects.filter(id=pk, user=user).delete()
    if not deleted:
        return Response(
            {"error": "Reading status not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(
        {"message": "Reading status removed."},
        status=status.HTTP_204_NO_CONTENT,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def nearby_owners(request, book_id):
    """
    Get list of users who own this book, are willing to barter,
    and are within a given radius (default 20 km).
    """

    book = get_object_or_404(
        BookCopy.objects.select_related("owner", "publication"), pk=book_id
    )
    radius_km = float(request.query_params.get("radius", 20))

    user_lat_val = getattr(request.user, "latitude", None)
    user_lon_val = getattr(request.user, "longitude", None)
    if not user_lat_val or not user_lon_val:
        return Response(
            {"error": "Your location is not set. Please update your profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_lat = float(user_lat_val)
    user_lon = float(user_lon_val)

    potential_owners = (
        BookCopy.objects.filter(
            publication=book.publication,
            is_for_barter=True,
        )
        .exclude(owner=request.user)
        .select_related("owner")
    )

    def haversine(lon1, lat1, lon2, lat2):
        """Calculate distance in km between two lat/lon points."""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return 6371 * c

    results = []
    for book_instance in potential_owners:
        owner = book_instance.owner
        owner_lat = getattr(owner, "latitude", None)
        owner_lon = getattr(owner, "longitude", None)
        if not owner_lat or not owner_lon:
            continue

        distance = haversine(
            user_lon, user_lat, float(owner_lon), float(owner_lat)
        )
        if distance <= radius_km:
            owner_data = UserBarterInfoSerializer(
                owner, context={"request": request}
            ).data
            owner_data["distance_km"] = round(distance, 2)
            results.append(owner_data)

    results.sort(key=lambda item: item["distance_km"])
    return Response({"owners": results}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def publication_recommendations(request):
    """
    Return sample publication recommendations for exploration.
    """
    limit = int(request.query_params.get("limit", 4))
    classifier = PublicationCategorizer()
    classification = classifier.classify({})

    results = []
    for idx in range(limit):
        results.append(
            {
                "id": str(idx),
                "title": f"Sample Recommendation {idx + 1}",
                "categoryScores": classification.category_scores,
                "tasteProfile": classification.taste_profile,
            }
        )

    return Response({"results": results}, status=status.HTTP_200_OK)


class OnboardingBookListView(generics.ListAPIView):
    """
    온보딩 과정에서 보여줄 책 목록은 "is_onboarding_choice=True"인 항목들만 반환합니다.
    """
    queryset = BookPublication.objects.filter(is_onboarding_choice=True)
    serializer_class = OnboardingBookSerializer
    permission_classes = [AllowAny]
    pagination_class = None # 페이지네이션 비활성화

class OnboardingAuthorListView(generics.ListAPIView):
    """
    온보딩 과정에서 보여줄 작가 목록은 "is_onboarding_choice=True"인 항목들만 반환합니다.
    """
    queryset = Author.objects.filter(is_onboarding_choice=True)
    serializer_class = OnboardingAuthorSerializer
    permission_classes = [AllowAny]
    pagination_class = None # 페이지네이션 비활성화

class OnboardingGenreListView(generics.ListAPIView):
    """
    온보딩 과정에서 보여줄 장르 목록은 "is_onboarding_choice=True"인 항목들만 반환합니다.
    """
    queryset = Genre.objects.filter(is_onboarding_choice=True)
    serializer_class = OnboardingGenreSerializer
    permission_classes = [AllowAny]
    pagination_class = None # 페이지네이션 비활성화
