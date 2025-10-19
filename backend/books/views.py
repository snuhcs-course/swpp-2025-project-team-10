from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Book, BookReview, BookWishlist
from .serializers import BookSerializer, BookReviewSerializer, BookWishlistSerializer


# books
@api_view(['GET'])
@permission_classes([AllowAny])
def list_books(request):
    """List all books."""
    books = Book.objects.all().order_by('-created_at')
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_book(request):
    """Allow authenticated users to add a book."""
    serializer = BookSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def book_detail_by_title(request, title):
    """Retrieve details of a single book by title."""
    book = get_object_or_404(Book, title=title)
    serializer = BookSerializer(book)
    return Response(serializer.data)


# reviews
@api_view(['GET'])
@permission_classes([AllowAny])
def list_reviews(request):
    """List all reviews (optionally filter by book title)."""
    title = request.query_params.get('bookTitle')
    if title:
        book = get_object_or_404(Book, title=title)
        reviews = book.reviews.all().order_by('-created_at')
    else:
        reviews = BookReview.objects.all().order_by('-created_at')

    serializer = BookReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request):
    """
    Add a review for a specific book.
    The frontend sends: bookTitle, authorName, content, imageUrls
    """
    book_title = request.data.get('bookTitle')
    if not book_title:
        return Response({'error': 'bookTitle is required.'}, status=status.HTTP_400_BAD_REQUEST)

    book = Book.objects.filter(title=book_title).first()
    if not book:
        # Automatically create a book entry if it doesn’t exist yet
        book = Book.objects.create(
            title=book_title,
            author_name=request.data.get('authorName', 'Unknown'),
            owner=request.user
        )

    serializer = BookReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(book=book, reviewer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_review_helpful(request, review_id):
    """Mark a review as helpful or remove the vote."""
    review = get_object_or_404(BookReview, id=review_id)
    user = request.user

    if review.helpful_votes.filter(id=user.id).exists():
        review.helpful_votes.remove(user)
        return Response({'message': 'Removed helpful vote.'})
    else:
        review.helpful_votes.add(user)
        return Response({'message': 'Marked review as helpful.'})


# wishlist
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_wishlist(request):
    """List all books in the user’s wishlist."""
    wishlist = BookWishlist.objects.filter(user=request.user).order_by('-priority')
    serializer = BookWishlistSerializer(wishlist, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist_by_title(request, title):
    """Add a book to the user’s wishlist using the book title."""
    book = get_object_or_404(Book, title=title)
    wishlist_item, created = BookWishlist.objects.get_or_create(user=request.user, book=book)

    if not created:
        return Response({'message': 'Book already in wishlist.'}, status=status.HTTP_200_OK)

    serializer = BookWishlistSerializer(wishlist_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
