from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, PostLike, CommentLike
from .serializers import PostSerializer, CommentSerializer


#list of all posts

@api_view(['GET'])
@permission_classes([AllowAny])  # anyone can view posts
def list_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

#create a new post

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    content = request.data.get('content')
    post_type = request.data.get('post_type', 'text')
    related_book_id = request.data.get('related_book_id')
    
    post = Post.objects.create(
        author=request.user,
        content=content,
        post_type=post_type,
        related_book_id=related_book_id
    )
    return Response({'id': post.id, 'content': post.content})

#like on a post

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Check if user already liked the post
    like, created = PostLike.objects.get_or_create(post=post, user=user)

    if not created:
        # User already liked -> maybe unlike
        like.delete()
        return Response({"liked": False, "likes_count": post.post_likes.count()})

    return Response({"liked": True, "likes_count": post.post_likes.count()})

# add comment on a specific post

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=400)
        comment = Comment.objects.create(post=post, author=request.user, content=content)
        return Response({'id': str(comment.id), 'content': comment.content, 'author': comment.author.username, 'written at': comment.created_at}, status=201)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

#like a specific comment. If already liked, then unlike it.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post__id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    like,created = CommentLike.objects.get_or_create(comment=comment, user=user)

    if not created:
        like.delete()
        return Response({"liked": False, "likes_count": comment.like_count}, status=status.HTTP_200_OK)

    return Response({"liked": True, "likes_count": comment.like_count}, status=status.HTTP_201_CREATED)


#list of comments

@api_view(['GET'])
@permission_classes([AllowAny])  # anyone can read comments
def list_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)
