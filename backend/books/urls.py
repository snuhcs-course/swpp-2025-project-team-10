"""
URL configuration for books app.
Maps URLs to views for book review endpoints.
"""

from django.urls import path

from .views import ReviewLikeView, UserReviewListCreateView

app_name = "books"

urlpatterns = [
    # User's book reviews
    path("reviews/", UserReviewListCreateView.as_view(), name="user-reviews"),
    # Like/unlike a review
    path(
        "reviews/<int:pk>/like/",
        ReviewLikeView.as_view(),
        name="review-like",
    ),
]
