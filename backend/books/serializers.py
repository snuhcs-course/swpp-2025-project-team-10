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
    publicationId = serializers.UUIDField(source="publication.id", read_only=True)
    
    class Meta:
        model = BookCopy
        fields = [
            "id",
            "title",
            "authorNames",
            "trade_status",
            "is_for_barter",
            "publicationId",

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
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, default=3)

    def update(self, instance, validated_data):
        """Update an existing review."""
        instance.book_title = validated_data.get("bookTitle", instance.book_title)
        instance.author_name = validated_data.get("authorName", instance.author_name)
        instance.content = validated_data.get("content", instance.content)
        instance.image_urls = validated_data.get("imageUrls", instance.image_urls)
        instance.rating = validated_data.get("rating", instance.rating)

        # Book ID (bookId) is optional
        book_id = validated_data.get("bookId")
        if book_id:
            try:
                instance.book = BookCopy.objects.get(pk=book_id)
            except BookCopy.DoesNotExist:
                pass  # ignore invalid bookId — keeps existing book

        instance.save()
        return instance


    def create(self, validated_data):
        """Create a new BookReview instance."""
        user = self.context["request"].user
        book_id = validated_data.get("bookId")
        
        # Try to find the book if bookId is provided
        book = None
        if book_id:
            try:
                book = BookCopy.objects.get(pk=book_id)
            except BookCopy.DoesNotExist:
                pass

        review = BookReview.objects.create(
            reviewer=user,
            book=book,
            book_title=validated_data["bookTitle"],
            author_name=validated_data.get("authorName", ""),
            content=validated_data["content"],
            image_urls=validated_data.get("imageUrls", []),
            rating=validated_data["rating"],
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
    """
    Serializer for user-owned book copies exposed via profile/library APIs.
    """
    
    publicationId = serializers.UUIDField(source='publication.id', read_only=True)
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
        allow_null=True
    )
    # Fields for creating a new BookPublication if needed
    book_isbn_10 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_isbn_13 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_publisher = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_published_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_title = serializers.CharField(write_only=True, required=False, allow_blank=True)  # ADD THIS
    book_authors = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
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
            "publicationId",
            #post
            "publication",
            #When a user adds a book that does not exist in BookPublication,
            #these fields are used to create a new BookPublication.
            "book_title",
            "book_authors",
            "book_isbn_10",
            "book_isbn_13",
            "book_publisher",
            "book_published_date",
            "book_description",


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

    def get_authors(self, obj):
        return list(obj.publication.authors.values_list("name", flat=True))

    def get_authors_display(self, obj):
        return self.get_authors(obj)

    def get_publisher_name(self, obj):
        publisher = obj.publication.publisher
        return publisher.name if publisher else None


    def get_cover_image(self, obj):
        publication = obj.publication

        if not publication.cover_image:
            return None
        request = self.context.get("request")
        url = publication.cover_image.url
        return request.build_absolute_uri(url) if request else url
    
    def get_publicationId(self, obj):
        return obj.publication.id if obj.publication else None


    def get_coverUrl(self, obj):
        return self.get_cover_image(obj)
    
    def validate(self, data):
        """
        Custom validation to check that either publication or book_title is provided
        """
        publication = data.get('publication')
        book_title = data.get('book_title')
        
        if not publication and not book_title:
            raise serializers.ValidationError(
                "Either 'publication' or 'book_title' must be provided"
            )
    
        return data


    def create(self, validated_data):
        # Check if publication is provided directly
        publication = validated_data.pop("publication", None)

        # Extract fields for creating new publication
        book_title = validated_data.pop("book_title", None)
        book_authors = validated_data.pop("book_authors", [])
        book_isbn_10 = validated_data.pop("book_isbn_10", "").strip()
        book_isbn_13 = validated_data.pop("book_isbn_13", "").strip()
        book_publisher = validated_data.pop("book_publisher", "").strip()
        book_published_date = validated_data.pop("book_published_date", "").strip()
        book_description = validated_data.pop("book_description", "").strip()

        # If no publication provided, try to find or create one
        if publication is None:
            if not book_title:
                raise serializers.ValidationError({"book_title": "Either 'publication' or 'book_title' must be provided"})
            
            # Try to find existing BookPublication by ISBN
            if book_isbn_13:
                publication = BookPublication.objects.filter(isbn_13=book_isbn_13).first()
            
            if not publication and book_isbn_10:
                publication = BookPublication.objects.filter(isbn_10=book_isbn_10).first()

            # If not found by ISBN, try by title (case-insensitive)
            if not publication:
                publication = BookPublication.objects.filter(
                    title__iexact=book_title
                ).first()

            # If still not found, create new BookPublication
            if not publication:
                # Handle publisher
                publisher_obj = None
                if book_publisher:
                    publisher_obj, _ = Publisher.objects.get_or_create(
                        name=book_publisher
                    )

                # Create publication
                publication = BookPublication.objects.create(
                    title=book_title,
                    isbn_10=book_isbn_10 or None,
                    isbn_13=book_isbn_13 or None,
                    publisher=publisher_obj,
                    publication_date=book_published_date or None,
                    description=book_description,
                )

                # Create and link authors
                if book_authors:
                    for author_name in book_authors:
                        author, _ = Author.objects.get_or_create(
                            name=author_name.strip()
                        )
                        publication.authors.add(author)

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


# --- Onboarding Serializers ---

class OnboardingBookSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title")

    class Meta:
        model = BookPublication
        fields = ["id", "name"]


class OnboardingAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class OnboardingGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]
