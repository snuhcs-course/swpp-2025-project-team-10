"""
Serializers for the social app.
"""

from books.models import BookWishlist
from rest_framework import serializers
from social.models import Comment, Post, CommentLike


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
    posterLocation = serializers.CharField(
        source="author.location", read_only=True
    )
    posterProfile = serializers.SerializerMethodField()
    bookTitle = serializers.SerializerMethodField()
    authorName = serializers.SerializerMethodField()
    content = serializers.CharField(read_only=True)
    imageUrls = serializers.SerializerMethodField()

    bookTitle = serializers.CharField(source="book_title", read_only=True)
    authorName = serializers.CharField(source="author_name", read_only=True)

    # New: bookId for direct bartering
    bookId = serializers.SerializerMethodField()

    # Engagement stats
    likeCount = serializers.IntegerField(source="like_count", read_only=True)
    commentCount = serializers.IntegerField(
        source="comment_count", read_only=True
    )

    # User-specific interaction states
    isLiked = serializers.SerializerMethodField()
    isBookmarked = serializers.SerializerMethodField()

    # Related book availability for barter button
    bookAvailableForBarter = serializers.SerializerMethodField()

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    comments = serializers.SerializerMethodField()

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
            "comments",
            "bookTitle",
            "authorName",
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
            "comments",
            "bookTitle",
            "authorName",
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

    # def get_bookTitle(self, obj):
    #     """Get book title from related_book if exists."""
    #     if obj.related_book:
    #         return obj.related_book.title
    #     return ""

    # def get_authorName(self, obj):
    #     """Get book author name from related_book if exists."""
    #     if obj.related_book:
    #         # Get the first author's name
    #         authors = obj.related_book.authors.all()
    #         if authors.exists():
    #             return authors.first().name
    #     return ""

    def get_imageUrls(self, obj):
        """Get image URLs for the post."""
        image_urls = []

        #Check for book cover image first
        if obj.book_cover_image:
            image_urls.append(obj.book_cover_image)

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
        book = obj.related_book
        
        is_for_barter = bool(getattr(book, "is_for_barter", False))
        trade_status = getattr(book, "trade_status", None)
        return (
            is_for_barter
            if trade_status is None
            else is_for_barter and trade_status == "available"
        )
    
    def get_comments(self, obj):
        """Get all comments related to the post."""
        comments = obj.comments.all().order_by('-created_at')
        from social.serializers import CommentSerializer  # Avoid circular import
        return CommentSerializer(comments, many=True, context=self.context).data


# class CommentSerializer(serializers.ModelSerializer):
#     """
#     Serializer for Comment model.
#     """

#     id = serializers.UUIDField(read_only=True)
#     authorName = serializers.CharField(source="author.username", read_only=True)
#     authorProfile = serializers.SerializerMethodField()

#     content = serializers.CharField()
#     createdAt = serializers.DateTimeField(source="created_at", read_only=True)
#     updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)


#     class Meta:
#         model = Comment
#         fields = [
#             "id",
#             "authorName",
#             "authorProfile",
#             "content",
#             "createdAt",
#             "updatedAt",
#         ]
#         read_only_fields = [
#             "id",
#             "authorName",
#             "authorProfile",
#             "createdAt",
#             "updatedAt",
#         ]
    
#     def get_authorProfile(self, obj):
#         """Get author's profile picture URL."""
#         return {
#             "username": obj.author.username,
#             "profile_picture": obj.author.profile_picture.url
#             if getattr(obj.author, "profile_picture", None)
#             else None,
#         }


class CommentSerializer(serializers.ModelSerializer):
    authorName = serializers.CharField(source='author.username', read_only=True)
    authorProfile = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'authorName',
            'content',
            'replies',
            'authorProfile',
            'like_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['author', 'authorProfile', 'created_at', 'updated_at', 'like_count', 'replies']

    def create(self, validated_data):
        """Automatically assign the author from the request user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

    def get_authorProfile(self, obj):
        """Get author's profile picture URL."""
        return {
            "username": obj.author.username,
            "profile_picture": obj.author.profile_picture.url
            if getattr(obj.author, "profile_picture", None)
            else None,
        }
    
    def get_like_count(self, obj):
        return obj.like_count  # calls your @property from the model


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
