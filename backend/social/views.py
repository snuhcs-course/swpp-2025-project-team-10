"""
Views for the social app.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social.models import Comment, Post, PostLike
from social.serializers import PostCreateSerializer, PostSerializer
from accounts.serializers import UserBarterInfoSerializer
from books.serializers import BookSummarySerializer
from notify.models import Notification
from barter.models import BarterRequest
from books.models import Book


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
    serializer = PostCreateSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"post": serializer.data}, status=status.HTTP_201_CREATED
        )

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
    else:
        # Create notification for the post author (if not self)
        if post.author_id != request.user.id:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type="post_liked",
                title="Your post was liked",
                message=f"{request.user.username} liked your post.",
                content_object=post,
            )

    # Return updated post
    serializer = PostSerializer(post, context={"request": request})

    return Response({"post": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    """
    Create a comment on a post and notify the post author.

    POST /posts/{post_id}/comments/
    Body: { "content": "..." }
    """
    content = request.data.get("content", "").strip()
    if not content:
        return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    comment = Comment.objects.create(post=post, author=request.user, content=content)

    # Notify post author (if not self)
    if post.author_id != request.user.id:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type="comment_received",
            title="New comment on your post",
            message=f"{request.user.username} commented: {content[:80]}",
            content_object=comment,
        )

    serializer = PostSerializer(post, context={"request": request})
    return Response({"post": serializer.data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def barter_post(request, post_id):
    """
    Create initial barter request from a post (Step 1: A → B).
    A requests B's book (from post) without specifying which book to offer yet.
    
    POST /posts/{post_id}/barter/
    Body:
      - message: str (optional)
    """
    try:
        post = Post.objects.select_related("author", "related_book").get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if not post.related_book:
        return Response(
            {"error": "This post has no related book to barter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    requested_book = post.related_book
    recipient = post.author
    requester = request.user

    # Verify requester cannot request their own book
    if requested_book.owner_id == requester.id:
        return Response(
            {"error": "Cannot request your own book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if owner allows barter for this book
    if not requested_book.is_for_barter:
        return Response(
            {"error": "This book is not available for barter (owner disabled trading)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if book is available for barter (not in pending trade)
    if requested_book.trade_status != "available":
        return Response(
            {"error": "This book is not available for barter (already in a pending trade)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Build message with requester's info
    msg = request.data.get("message")
    if not msg:
        parts = [
            f"Hi {recipient.username}, I'd like to barter for your '{requested_book.title}'."
        ]
        if requester.location:
            parts.append(f"My location: {requester.location}")
        msg = "\n".join(parts)

    # Create initial barter request (no offered_book yet)
    # Mark requested_book as not_available while barter is pending
    requested_book.trade_status = "not_available"
    requested_book.save(update_fields=["trade_status"])

    barter = BarterRequest.objects.create(
        requester=requester,
        recipient=recipient,
        offered_book=None,  # Will be set later by recipient in counter-proposal
        requested_book=requested_book,
        message=msg,
    )

    # Notify recipient
    Notification.objects.create(
        recipient=recipient,
        sender=requester,
        notification_type="barter_request",
        title="New barter request",
        message=f"{requester.username} wants to trade for '{requested_book.title}'.",
        content_object=barter,
    )

    from barter.serializers import BarterRequestSerializer
    serializer = BarterRequestSerializer(barter, context={"request": request})
    return Response({"barter": serializer.data}, status=status.HTTP_201_CREATED)