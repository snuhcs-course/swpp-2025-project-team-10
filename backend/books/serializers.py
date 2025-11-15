"""
Serializers for the books app.
Handles book reviews and related data serialization.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Book, BookReview, BookCollection, ReadingStatus

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for BookReview model matching frontend expectations.
    Used for GET requests to return review data.
    """

    # Frontend expects these exact field names
    id = serializers.IntegerField(read_only=True)
    bookTitle = serializers.CharField(source="book_title", read_only=True)
    authorName = serializers.CharField(source="author_name", read_only=True)
    userName = serializers.CharField(
        source="reviewer.username", read_only=True
    )
    userId = serializers.IntegerField(source="reviewer.id", read_only=True)
    userProfile = serializers.SerializerMethodField()
    content = serializers.CharField(read_only=True)
    imageUrls = serializers.ListField(
        source="image_urls", read_only=True, child=serializers.URLField()
    )
    likeCount = serializers.IntegerField(source="like_count", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    isLiked = serializers.SerializerMethodField()

    class Meta:
        model = BookReview
        fields = [
            "id",
            "bookTitle",
            "authorName",
            "userId",
            "userName",
            "userProfile",
            "content",
            "imageUrls",
            "likeCount",
            "createdAt",
            "isLiked",
        ]

    def get_userProfile(self, obj):
        """Get user profile picture URL."""
        if obj.reviewer.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(
                    obj.reviewer.profile_picture.url
                )
            return obj.reviewer.profile_picture.url
        return None

    def get_isLiked(self, obj):
        """Check if the current user has liked this review."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(id=request.user.id).exists()
        return False


class BookSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Book objects used in profile/barter payloads.
    """

    authorNames = serializers.CharField(source="author_names", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "authorNames",
            "trade_status",
            "is_for_barter",
        ]


class CreateReviewSerializer(serializers.Serializer):
    """
    Serializer for creating new reviews.
    Matches frontend POST request format.
    """

    bookTitle = serializers.CharField(max_length=200)
    authorName = serializers.CharField(max_length=200, allow_blank=True)
    content = serializers.CharField()
    imageUrls = serializers.ListField(
        child=serializers.URLField(), required=False, default=list
    )

    def create(self, validated_data):
        """Create a new BookReview instance."""
        user = self.context["request"].user

        review = BookReview.objects.create(
            reviewer=user,
            book_title=validated_data["bookTitle"],
            author_name=validated_data.get("authorName", ""),
            content=validated_data["content"],
            image_urls=validated_data.get("imageUrls", []),
        )
        return review

    def to_representation(self, instance):
        """Return the created review in the same format as ReviewSerializer."""
        serializer = ReviewSerializer(instance, context=self.context)
        return serializer.data


class ReviewLikeResponseSerializer(serializers.Serializer):
    """
    Serializer for like/unlike response.
    Returns the updated review with new like count.
    """

    review = ReviewSerializer(read_only=True)

    class Meta:
        fields = ["review"]

class BookSerializer(serializers.ModelSerializer):

    # Make owner read-only so it's set automatically in the view
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "authors",
            "publisher",
            "publication_date",
            "isbn_13",
            "description",
            "cover_image",
            "is_for_barter",
            "owner",
        ]
        read_only_fields = ['id', 'owner']  # owner is set in the view

class BookCollectionSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    book_count = serializers.ReadOnlyField()

    class Meta:
        model = BookCollection
        fields = [
            "id", "name", "description", "is_public",
            "books", "book_count", "created_at", "updated_at"
        ]

class ReadingStatusSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    # Explicitly use PrimaryKeyRelatedField for writing and make it WRITE_ONLY
    # This clearly documents that 'book' is only for input (POST/PATCH)
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True
    )

    class Meta:
        model = ReadingStatus
        fields = [
            "id",
            "book", #Write-only for input ID
            "book_title", #Read-only for output title
            "status",
            "pages_read",
            "start_date",
            "finish_date",
            "personal_rating",
            "notes",
        ]