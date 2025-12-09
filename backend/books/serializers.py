"""
Serializers for the books app.
Handles book reviews and related data serialization.
"""

import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    BookCollection,
    BookCopy,
    Author,
    Genre,
    BookPublication,
    BookReview,
    ReadingStatus,
    Author,
    Publisher,
)

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for BookReview model matching frontend expectations.
    Used for GET requests to return review data.
    """

    # Frontend expects these exact field names
    id = serializers.IntegerField(read_only=True)
    bookId = serializers.SerializerMethodField()
    bookTitle = serializers.CharField(source="book_title", read_only=True)
    authorName = serializers.CharField(source="author_name", read_only=True)
    userName = serializers.CharField(
        source="reviewer.username", read_only=True
    )
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
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
            "bookId",
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
            "rating", # Added rating field
        ]

    def get_bookId(self, obj):
        """Get book ID if review is linked to a book."""
        if obj.book:
            return str(obj.book.id)
        return None

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
        model = BookCopy
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

    bookId = serializers.UUIDField(required=False, allow_null=True)
    bookTitle = serializers.CharField(max_length=200)
    authorName = serializers.CharField(max_length=200, allow_blank=True)
    content = serializers.CharField()
    imageUrls = serializers.ListField(
        child=serializers.URLField(), required=False, default=list
    )


    def create(self, validated_data):
        """Create a new BookReview instance."""
        user = self.context["request"].user
        book_id = validated_data.get("bookId")
        book_title = validated_data.get("bookTitle")
        author_name = validated_data.get("authorName", "")
        content = validated_data["content"]
        image_urls = validated_data.get("imageUrls", [])

        # Try to find the book if bookId is provided
        book = None
        if book_id:
            try:
                book = BookCopy.objects.get(pk=book_id)
            except BookCopy.DoesNotExist:
                pass

        # book_title은 반드시 값이 있어야 함
        if not book_title:
            if book:
                book_title = book.title
            else:
                raise serializers.ValidationError({"bookTitle": "This field is required."})

        review = BookReview.objects.create(
            reviewer=user,
            book=book,
            book_title=book_title,
            author_name=author_name,
            content=content,
            image_urls=image_urls,
        )
        return review

    def update(self, instance, validated_data):
        """Update an existing BookReview instance."""
        # reviewer는 변경 불가, 나머지 필드만 업데이트
        book_id = validated_data.get("bookId", None)
        book_title = validated_data.get("bookTitle", instance.book_title)
        author_name = validated_data.get("authorName", instance.author_name)
        content = validated_data.get("content", instance.content)
        image_urls = validated_data.get("imageUrls", instance.image_urls)

        # bookId가 있으면 book 객체로 변환
        book = instance.book
        if book_id:
            try:
                book = BookCopy.objects.get(pk=book_id)
            except BookCopy.DoesNotExist:
                book = None

        # book_title은 반드시 값이 있어야 함
        if not book_title:
            if book:
                book_title = book.title
            else:
                raise serializers.ValidationError({"bookTitle": "This field is required."})

        instance.book = book
        instance.book_title = book_title
        instance.author_name = author_name
        instance.content = content
        instance.image_urls = image_urls
        instance.save()
        return instance

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
    """
    Serializer for user-owned book copies exposed via profile/library APIs.
    """

    owner = serializers.ReadOnlyField(source="owner.username")
    ownerId = serializers.IntegerField(source="owner.id", read_only=True)
    title = serializers.CharField(read_only=True)
    authors = serializers.SerializerMethodField()
    authors_display = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    author = serializers.CharField(source="author_names", read_only=True)
    coverUrl = serializers.SerializerMethodField(read_only=True)
    publication_date = serializers.DateField(
        source="publication.publication_date", read_only=True
    )
    isbn = serializers.CharField(source="publication.isbn_13", read_only=True)
    description = serializers.CharField(
        source="publication.description", read_only=True
    )
    cover_image = serializers.SerializerMethodField()
    owner_notes = serializers.CharField(required=False, allow_blank=True)
    publication = serializers.PrimaryKeyRelatedField(
        queryset=BookPublication.objects.all(),
        write_only=True,
        required=False,
    )
    publicationId = serializers.UUIDField(source="publication.id", read_only=True,)

    class Meta:
        model = BookCopy
        fields = [
            "id",
            "title",
            "authors",
            "authors_display",
            "author",
            "publisher_name",
            "publication_date",
            "isbn",
            "description",
            "cover_image",
            "coverUrl",
            "is_for_barter",
            "owner_notes",
            "trade_status",
            "owner",
            "ownerId",
            #post
            "publication",
            "publicationId",
        ]
        read_only_fields = [
            "id",
            "owner",
            "ownerId",
            "title",
            "authors",
            "authors_display",
            "author",
            "publisher_name",
            "publication_date",
            "isbn",
            "description",
            "cover_image",
            "coverUrl",
            "trade_status",
            "publicationId",
        ]
        extra_kwargs = {"publication": {"write_only": True}}
    def get_publicationId(self, obj):
        return obj.publication.id if obj.publication else None
    def get_authors(self, obj):
        return list(obj.publication.authors.values_list("name", flat=True))

    def get_authors_display(self, obj):
        return self.get_authors(obj)

    def get_publisher_name(self, obj):
        publisher = obj.publication.publisher
        return publisher.name if publisher else None


    def get_cover_image(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get("request")
        url = obj.cover_image.url
        return request.build_absolute_uri(url) if request else url

    def get_coverUrl(self, obj):
        return self.get_cover_image(obj)

    def create(self, validated_data):
        publication = validated_data.pop("publication", None)
        if publication is None:
            raise serializers.ValidationError(
                {"publication": "This field is required."}
            )
        return BookCopy.objects.create(
            publication=publication,
            **validated_data,
        )


class BookCollectionSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    book_count = serializers.ReadOnlyField()

    class Meta:
        model = BookCollection
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "books",
            "book_count",
            "created_at",
            "updated_at",
        ]


class ReadingStatusSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book = serializers.PrimaryKeyRelatedField(
        queryset=BookCopy.objects.all(), write_only=True
    )

    class Meta:
        model = ReadingStatus
        fields = [
            "id",
            "book",
            "book_title",
            "status",
            "pages_read",
            "start_date",
            "finish_date",
            "personal_rating",
            "notes",
        ]
