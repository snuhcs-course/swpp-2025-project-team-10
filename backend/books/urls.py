"""
URL configuration for books app.
Maps URLs to views for book review endpoints.
"""

from django.urls import path

from .views import (
    ReviewLikeView,
    UserReviewListCreateView,
    toggle_book_for_barter,
    toggle_wishlist,
    user_books_list,
    user_wishlist_list,
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
    # User's books list
    path("books/", user_books_list, name="user-books-list"),
    # User's wishlist
    path("wishlist/", user_wishlist_list, name="user-wishlist-list"),
    # Add/remove book from wishlist
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
]
