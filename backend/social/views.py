"""
Views for the social app.
"""

from barter.models import BarterRequest
from notify.models import Notification
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.models import Comment, Post, PostLike
from social.serializers import PostCreateSerializer, PostSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home_feed(request):
    """
    Get the home feed with all public posts.

    GET /home/
    """

    posts = (
        Post.objects.filter(is_public=True)
        .select_related("author", "related_book", "related_book__publication")
        .prefetch_related("related_book__publication__authors", "likes")
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
    """

    try:
        post = (
            Post.objects.select_related(
                "author", "related_book", "related_book__publication"
            )
            .prefetch_related("related_book__publication__authors", "likes")
            .get(id=post_id)
        )
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )

    like, created = PostLike.objects.get_or_create(
        post=post, user=request.user
    )

    if not created:
        like.delete()
    elif post.author_id != request.user.id:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type="post_liked",
            title="Your post was liked",
            message=f"{request.user.username} liked your post.",
            content_object=post,
        )

    serializer = PostSerializer(post, context={"request": request})
    return Response({"post": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    """
    Create a comment on a post and notify the post author.
    """

    content = request.data.get("content", "").strip()
    if not content:
        return Response(
            {"error": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )

    comment = Comment.objects.create(
        post=post, author=request.user, content=content
    )
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
    Create initial barter request from a post (Step 1: requester → recipient).
    """

    try:
        post = Post.objects.select_related(
            "author", "related_book", "related_book__publication"
        ).get(pk=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if not post.related_book:
        return Response(
            {"error": "This post has no related book to barter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    requested_book = post.related_book
    recipient = post.author
    requester = request.user

    if requested_book.owner_id == requester.id:
        return Response(
            {"error": "Cannot request your own book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if not requested_book.is_for_barter:
        return Response(
            {
                "error": (
                    "This book is not available for barter "
                    "(owner disabled trading)"
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requested_book.trade_status != "available":
        return Response(
            {
                "error": (
                    "This book is not available for barter "
                    "(already in a pending trade)"
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    message = request.data.get("message")
    if not message:
        parts = [
            f"Hi {recipient.username}, I'd like to barter for '{requested_book.title}'."
        ]
        if requester.location:
            parts.append(f"My location: {requester.location}")
        message = " ".join(parts)

    requested_book.trade_status = "not_available"
    requested_book.save(update_fields=["trade_status"])

    barter = BarterRequest.objects.create(
        requester=requester,
        recipient=recipient,
        offered_book=None,
        requested_book=requested_book,
        message=message,
    )

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
    return Response(
        {"barter": serializer.data}, status=status.HTTP_201_CREATED
    )
