"""
URL configuration for books app.
Maps URLs to views for book review endpoints.
"""

from django.urls import path

from .views import (
    ReviewLikeView,
    UserReviewListCreateView,
    nearby_owners,
    toggle_book_for_barter,
    toggle_wishlist,
)

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
    # Toggle wishlist (bookmark a book)
    path(
        "books/<uuid:book_id>/wishlist/",
        toggle_wishlist,
        name="toggle-wishlist",
    ),
    # Toggle barter availability for owned book
    path(
        "books/<uuid:book_id>/toggle-barter/",
        toggle_book_for_barter,
        name="toggle-barter",
    ),
    # Get nearby owners of a book
    path(
        "books/<uuid:book_id>/nearby-owners/",
        nearby_owners,
        name="nearby-owners",
    ),
]
