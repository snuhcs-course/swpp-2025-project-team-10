"""
Serializers for the social app.
"""

from rest_framework import serializers

from social.models import Post


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model matching frontend expectations.
    Used for GET requests to return post data in the home feed.
    """

    # Frontend expects these exact field names (camelCase)
    id = serializers.IntegerField(read_only=True)
    posterName = serializers.CharField(
        source="author.username", read_only=True
    )
    posterProfile = serializers.SerializerMethodField()
    bookTitle = serializers.SerializerMethodField()
    authorName = serializers.SerializerMethodField()
    content = serializers.CharField(read_only=True)
    imageUrls = serializers.SerializerMethodField()
    likeCount = serializers.IntegerField(source="like_count", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    isLiked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "posterName",
            "posterProfile",
            "bookTitle",
            "authorName",
            "content",
            "imageUrls",
            "likeCount",
            "createdAt",
            "isLiked",
        ]
        read_only_fields = ["id", "posterName", "posterProfile", "likeCount", "isLiked", "createdAt"]

    def get_posterProfile(self, obj):
        """Get poster's profile picture URL."""
        if obj.author.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(
                    obj.author.profile_picture.url
                )
            return obj.author.profile_picture.url
        return None

    def get_bookTitle(self, obj):
        """Get book title from related_book if exists."""
        if obj.related_book:
            return obj.related_book.title
        return ""

    def get_authorName(self, obj):
        """Get book author name from related_book if exists."""
        if obj.related_book:
            # Get the first author's name
            authors = obj.related_book.authors.all()
            if authors.exists():
                return authors.first().name
        return ""

    def get_imageUrls(self, obj):
        """Get image URLs for the post."""
        image_urls = []
        if obj.image:
            request = self.context.get("request")
            if request:
                image_urls.append(request.build_absolute_uri(obj.image.url))
            else:
                image_urls.append(obj.image.url)
        return image_urls

    def get_isLiked(self, obj):
        """Check if the current user has liked this post."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class FeedResponseSerializer(serializers.Serializer):
    """
    Serializer for feed response matching frontend expectations.
    """

    results = PostSerializer(many=True, read_only=True)


class LikeResponseSerializer(serializers.Serializer):
    """
    Serializer for like response matching frontend expectations.
    """

    post = PostSerializer(read_only=True)

class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new posts.
    Accepts content, post_type, related_book, image, and is_public.
    """

    class Meta:
        model = Post
        fields = ["content", "post_type", "related_book", "image", "is_public"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Post.objects.create(author=user, **validated_data)


