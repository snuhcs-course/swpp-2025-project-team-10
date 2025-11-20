"""
Tests for social app serializers.
"""

import pytest
from books.models import BookCopy, BookPublication, Publisher
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from social.models import Post
from social.serializers import PostSerializer

User = get_user_model()


@pytest.mark.django_db
def test_post_serializer_with_profile_picture():
    """Test PostSerializer includes profile picture URL."""
    user = User.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="pass123",
        first_name="Test",
        last_name="User",
    )

    # Create a fake profile picture
    profile_pic = SimpleUploadedFile(
        name="test_image.jpg", content=b"", content_type="image/jpeg"
    )
    user.profile_picture = profile_pic
    user.save()

    post = Post.objects.create(
        author=user, content="Test post", post_type="book_review"
    )

    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = user

    serializer = PostSerializer(post, context={"request": request})
    data = serializer.data

    assert "posterProfile" in data
    assert data["posterProfile"] is not None


@pytest.mark.django_db
def test_post_serializer_without_profile_picture():
    """Test PostSerializer when user has no profile picture."""
    user = User.objects.create_user(
        username="testuser2",
        email="test2@test.com",
        password="pass123",
        first_name="Test",
        last_name="User",
    )

    post = Post.objects.create(
        author=user, content="Test post", post_type="text"
    )

    serializer = PostSerializer(post)
    data = serializer.data

    assert "posterProfile" in data
    assert data["posterProfile"] is None


@pytest.mark.django_db
def test_post_serializer_with_book():
    """Test PostSerializer with related book."""
    user = User.objects.create_user(
        username="testuser3",
        email="test3@test.com",
        password="pass123",
        first_name="Test",
        last_name="User",
    )

    publisher = Publisher.objects.create(name="Test Publisher")
    publication = BookPublication.objects.create(
        title="Test Book",
        publisher=publisher,
    )
    book = BookCopy.objects.create(
        publication=publication, owner=user, is_for_barter=True
    )

    post = Post.objects.create(
        author=user,
        content="Test post",
        post_type="barter_success",
        related_book=book,
    )

    serializer = PostSerializer(post)
    data = serializer.data

    assert "bookId" in data
    assert data["bookId"] == str(book.id)


@pytest.mark.django_db
def test_post_serializer_without_book():
    """Test PostSerializer without related book."""
    user = User.objects.create_user(
        username="testuser4",
        email="test4@test.com",
        password="pass123",
        first_name="Test",
        last_name="User",
    )

    post = Post.objects.create(
        author=user, content="Test post", post_type="text"
    )

    serializer = PostSerializer(post)
    data = serializer.data

    assert "bookId" in data
    assert data["bookId"] is None
