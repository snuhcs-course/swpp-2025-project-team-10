"""
Serializers for the books app.
Handles book reviews and related data serialization.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Book, BookReview, BookCollection, ReadingStatus, Author, Publisher

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


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.CharField(write_only=True, required=False)
    publisher_name = serializers.CharField(write_only=True, required=False)
    owner = serializers.StringRelatedField(read_only=True)
    authors_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "authors",
            "authors_display",
            "publisher_name",
            "isbn",
            "description",
            "cover_image",
            "is_for_barter",
            "owner",
        ]
        extra_kwargs = {
            "publisher": {"required": False},
        }
    
    def get_authors_display(self, obj):
        return [author.name for author in obj.authors.all()]
    
    def create(self, validated_data):
        # print("=" * 50)
        # print("CREATE METHOD IS BEING CALLED!!!")
        # print(f"validated_data: {validated_data}")
        # print("=" * 50)

        publisher_name = validated_data.pop("publisher_name", None)
        if publisher_name:
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            validated_data["publisher"] = publisher
    
        authors_str = validated_data.pop("authors", "")
        # print(f"DEBUG: authors_str = '{authors_str}'")  # Debug line
        # print(f"DEBUG: validated_data = {validated_data}")  # Debug line
    
        book = Book.objects.create(**validated_data)
        # print(f"DEBUG: Book created with id {book.id}")  # Debug line
    
        if authors_str:
            for author_name in [a.strip() for a in authors_str.split(',') if a.strip()]:
                author_obj, _ = Author.objects.get_or_create(name=author_name)
                book.authors.add(author_obj)
                print(f"DEBUG: Added author '{author_name}'")  # Debug line
        else:
            print("DEBUG: authors_str is empty or None")  # Debug line
    
        # Check authors before returning
        reloaded_book = Book.objects.prefetch_related('authors').get(pk=book.pk)
        # print(f"DEBUG: Authors count: {reloaded_book.authors.count()}")  # Debug line
        # print(f"DEBUG: Authors: {[a.name for a in reloaded_book.authors.all()]}")  # Debug line
    
        return reloaded_book
    
    def update(self, instance, validated_data):
        publisher_name = validated_data.pop("publisher_name", None)
        if publisher_name:
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            instance.publisher = publisher
        
        authors_str = validated_data.pop('authors', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if authors_str is not None:
            instance.authors.clear()
            for author_name in [a.strip() for a in authors_str.split(',') if a.strip()]:
                author_obj, _ = Author.objects.get_or_create(name=author_name)
                instance.authors.add(author_obj)
        
        # Reload the instance with authors prefetched
        return Book.objects.prefetch_related('authors').get(pk=instance.pk)

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