"""
Serializers for the social app.
"""

from rest_framework import serializers

from social.models import Post
from books.models import BookWishlist


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model matching frontend expectations.
    Used for GET requests to return post data in the home feed.
    Includes action buttons: like, comment, bookmark, barter.
    """

    # Frontend expects these exact field names (camelCase)
    id = serializers.IntegerField(read_only=True)
    posterName = serializers.CharField(
        source="author.username", read_only=True
    )
    # Added: posterId and posterLocation for profile navigation
    posterId = serializers.IntegerField(source="author.id", read_only=True)
    posterLocation = serializers.CharField(source="author.location", read_only=True)
    posterProfile = serializers.SerializerMethodField()
    bookTitle = serializers.SerializerMethodField()
    authorName = serializers.SerializerMethodField()
    content = serializers.CharField(read_only=True)
    imageUrls = serializers.SerializerMethodField()

    # New: bookId for direct bartering
    bookId = serializers.SerializerMethodField()

    # Engagement stats
    likeCount = serializers.IntegerField(source="like_count", read_only=True)
    commentCount = serializers.IntegerField(source="comment_count", read_only=True)

    # User-specific interaction states
    isLiked = serializers.SerializerMethodField()
    isBookmarked = serializers.SerializerMethodField()

    # Related book availability for barter button
    bookAvailableForBarter = serializers.SerializerMethodField()

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "posterId",
            "posterName",
            "posterLocation",
            "posterProfile",
            "bookTitle",
            "authorName",
            "content",
            "imageUrls",
            "bookId",
            "likeCount",
            "commentCount",
            "isLiked",
            "isBookmarked",
            "bookAvailableForBarter",
            "createdAt",
        ]
        read_only_fields = [
            "id",
            "posterId",
            "posterName",
            "posterLocation",
            "posterProfile",
            "likeCount",
            "commentCount",
            "isLiked",
            "isBookmarked",
            "bookAvailableForBarter",
            "createdAt",
            "bookId",
        ]
    def get_bookId(self, obj):
        """Return the related book's id if exists, else None."""
        if obj.related_book:
            return str(obj.related_book.id)
        return None

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

    def get_isBookmarked(self, obj):
        """Check if the current user has wishlisted (bookmarked) the related book."""
        request = self.context.get("request")
        if not obj.related_book:
            return False
        if request and request.user.is_authenticated:
            return BookWishlist.objects.filter(
                user=request.user, book=obj.related_book
            ).exists()
        return False

    def get_bookAvailableForBarter(self, obj):
        """Return whether the related book is currently available for barter."""
        if not obj.related_book:
            return False
        # Check both is_for_barter (owner wants to trade) and trade_status (not locked in trade)
        return ( 
            obj.related_book.is_for_barter and 
            obj.related_book.trade_status == "available"
        )


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
