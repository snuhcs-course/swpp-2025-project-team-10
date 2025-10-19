from rest_framework import serializers
from .models import Book, BookReview, BookWishlist


class BookSerializer(serializers.ModelSerializer):
    author_names = serializers.ReadOnlyField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'subtitle', 'author_names', 'description',
            'language', 'condition', 'availability', 'is_for_barter',
            'owner_username', 'cover_image', 'created_at'
        ]


class BookReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BookReview
        fields = [
            'id', 'book_title', 'reviewer_username',
            'rating', 'title', 'content',
            'helpful_count', 'created_at'
        ]
        read_only_fields = ['book_title', 'reviewer_username', 'helpful_count', 'created_at']


class BookWishlistSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BookWishlist
        fields = ['id', 'book', 'book_title', 'priority', 'notes', 'created_at']
        read_only_fields = ['book_title', 'created_at']