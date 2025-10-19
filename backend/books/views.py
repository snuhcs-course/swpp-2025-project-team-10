"""
Views for the books app.
Handles book review API endpoints.
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BookReview, ReviewHelpfulVote
from .serializers import (
    CreateReviewSerializer,
    ReviewLikeResponseSerializer,
    ReviewSerializer,
)

User = get_user_model()


class UserReviewListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating user's book reviews.

    GET /library/reviews/ - List all reviews by the authenticated user
    POST /library/reviews/ - Create a new review
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == "POST":
            return CreateReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        """Return only the authenticated user's reviews."""
        return BookReview.objects.filter(
            reviewer=self.request.user
        ).select_related("reviewer")

    @extend_schema(
        summary="List User's Reviews",
        description="Get all book reviews created by the authenticated user",
        responses={
            200: OpenApiResponse(
                description="List of user's reviews",
                response=ReviewSerializer(many=True),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """List all reviews by the authenticated user."""
        queryset = self.get_queryset()
        serializer = ReviewSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"results": serializer.data})

    @extend_schema(
        summary="Create New Review",
        description="Create a new book review",
        request=CreateReviewSerializer,
        responses={
            201: OpenApiResponse(
                description="Review created successfully",
                response=ReviewSerializer,
            ),
            400: OpenApiResponse(description="Invalid data"),
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new book review."""
        serializer = CreateReviewSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                serializer.to_representation(review),
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewLikeView(APIView):
    """
    API endpoint for liking/unliking a review.

    POST /library/reviews/{id}/like/ - Toggle like on a review
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Like/Unlike Review",
        description="Toggle like on a book review. If already liked, "
        "it will unlike. If not liked, it will like.",
        responses={
            200: OpenApiResponse(
                description="Like toggled successfully",
                response=ReviewLikeResponseSerializer,
            ),
            404: OpenApiResponse(description="Review not found"),
        },
    )
    def post(self, request, pk):
        """Toggle like on a review."""
        try:
            review = BookReview.objects.select_related("reviewer").get(pk=pk)
        except BookReview.DoesNotExist:
            return Response(
                {"error": "Review not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user already liked this review
        existing_like = ReviewHelpfulVote.objects.filter(
            review=review, user=request.user
        ).first()

        if existing_like:
            # Unlike: remove the like
            existing_like.delete()
        else:
            # Like: add a new like
            ReviewHelpfulVote.objects.create(review=review, user=request.user)

        # Return updated review data
        serializer = ReviewSerializer(review, context={"request": request})
        return Response({"review": serializer.data}, status=status.HTTP_200_OK)
