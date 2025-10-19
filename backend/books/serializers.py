"""
Serializers for the books app.
Handles book reviews and related data serialization.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import BookReview, ReviewHelpfulVote

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
    userProfile = serializers.SerializerMethodField()
    content = serializers.CharField(read_only=True)
    imageUrls = serializers.ListField(
        source="image_urls", read_only=True, child=serializers.URLField()
    )
    likeCount = serializers.IntegerField(source="like_count", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = BookReview
        fields = [
            "id",
            "bookTitle",
            "authorName",
            "userName",
            "userProfile",
            "content",
            "imageUrls",
            "likeCount",
            "createdAt",
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
