"""
Views for the social app.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social.models import Post, PostLike
from social.serializers import PostSerializer, PostCreateSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home_feed(request):
    """
    Get the home feed with all public posts.

    GET /home/

    Returns:
        {
            "results": [
                {
                    "id": 1,
                    "posterName": "username",
                    "posterProfile": "url",
                    "bookTitle": "Book Title",
                    "authorName": "Author Name",
                    "content": "Post content",
                    "imageUrls": ["url1", "url2"],
                    "likeCount": 10,
                    "createdAt": "2025-10-10T09:00:00Z",
                    "isLiked": false
                },
                ...
            ]
        }
    """
    # Get all public posts ordered by creation date (newest first)
    posts = (
        Post.objects.filter(is_public=True)
        .select_related("author", "related_book")
        .prefetch_related("related_book__authors", "likes")
        .order_by("-created_at")
    )

    serializer = PostSerializer(posts, many=True, context={"request": request})

    return Response({"results": serializer.data}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Create a new post with optional image upload.

    POST /posts/create/
    Content-Type: multipart/form-data
    Fields:
        - content: str
        - post_type: str (optional, default "text")
        - related_book: int (optional, book ID)
        - image: file (optional)
        - is_public: boolean (optional, default True)
    """
    serializer = PostCreateSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        serializer.save()
        return Response({"post": serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    """
    Like or unlike a post.

    POST /posts/{post_id}/like/

    Args:
        post_id: Integer ID of the post

    Returns:
        {
            "post": {
                "id": 1,
                "posterName": "username",
                ...
                "isLiked": true
            }
        }
    """
    try:
        post = (
            Post.objects.select_related("author", "related_book")
            .prefetch_related("related_book__authors", "likes")
            .get(id=post_id)
        )
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Toggle like
    like, created = PostLike.objects.get_or_create(
        post=post, user=request.user
    )

    if not created:
        # Unlike if already liked
        like.delete()

    # Return updated post
    serializer = PostSerializer(post, context={"request": request})

    return Response({"post": serializer.data}, status=status.HTTP_200_OK)
