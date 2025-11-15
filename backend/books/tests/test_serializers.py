"""
Unit tests for books app serializers.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from books.models import BookReview
from books.serializers import ReviewSerializer

User = get_user_model()


@pytest.mark.django_db
def test_review_serializer_with_profile_picture():
    """Test ReviewSerializer includes user profile picture."""
    user = User.objects.create_user(
        username="reviewer",
        email="review@example.com",
        password="testpass123",
    )
    
    # Add profile picture
    profile_pic = SimpleUploadedFile(
        name='test.jpg',
        content=b'',
        content_type='image/jpeg'
    )
    user.profile_picture = profile_pic
    user.save()
    
    review = BookReview.objects.create(
        reviewer=user,
        book_title="Test Book",
        author_name="Test Author",
        content="Test content"
    )
    
    serializer = ReviewSerializer(review, context={'request': None})
    data = serializer.data
    
    assert 'userProfile' in data
    assert data['userProfile'] is not None


@pytest.mark.django_db
def test_review_serializer_without_profile_picture():
    """Test ReviewSerializer when user has no profile picture."""
    user = User.objects.create_user(
        username="reviewer2",
        email="review2@example.com",
        password="testpass123",
    )
    
    review = BookReview.objects.create(
        reviewer=user,
        book_title="Test Book",
        author_name="Test Author",
        content="Test content"
    )
    
    serializer = ReviewSerializer(review)
    data = serializer.data
    
    assert 'userProfile' in data
    assert data['userProfile'] is None
