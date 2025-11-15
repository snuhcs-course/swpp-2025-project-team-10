"""
URL configuration for books app.
Maps URLs to views for book review endpoints.
"""

from django.urls import path

from .views import (
    ReviewLikeView,
    UserReviewListCreateView,
    user_profile_detail,
    toggle_book_for_barter,
    toggle_wishlist,
    user_books_list,
    user_books_list_by_id,
    user_wishlist_list,
    user_wishlist_by_id,
    user_reviews_by_id,
    book_list,
    book_detail,
    collection_list_view,
    modify_collection_books, reading_status_view, modify_reading_status,
    )


from .book_search_api import book_search

app_name = "books"

urlpatterns = [
    # User's book reviews
    path("reviews/", UserReviewListCreateView.as_view(), name="user-reviews"),
    # Other user's book reviews by ID
    path(
        "reviews/<int:user_id>/",
        user_reviews_by_id,
        name="user-reviews-by-id",
    ),
    # Like/unlike a review
    path(
        "reviews/<int:pk>/like/",
        ReviewLikeView.as_view(),
        name="review-like",
    ),
    # Other user's profile (basic)
    path(
        "profile/<int:user_id>/",
        user_profile_detail,
        name="user-profile-by-id",
    ),
    # User's books list
    path("books/", user_books_list, name="user-books-list"),
    # Other user's books by ID
    path("books/<int:user_id>/", user_books_list_by_id, name="user-books-list-by-id"),
   
    # User's wishlist
    path("wishlist/", user_wishlist_list, name="user-wishlist-list"),
    # Other user's wishlist by ID
    path(
        "wishlist/<int:user_id>/",
        user_wishlist_by_id,
        name="user-wishlist-by-id",
    ),
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

    #Book search API
    path("books/search/", book_search, name="book-search"),

    #User's book list.
    path("books/", book_list, name="books-list"),

    #Book detail API.
    path("books/<uuid:book_id>/", book_detail, name="book-detail"),

    #Collection API
    path("collections/", collection_list_view, name="collection-view"),  # List or modify collections
    path("collections/<int:pk>/", modify_collection_books, name="collection-detail"),  # Single collection actions

    # Reading status API
    path("reading-status/", reading_status_view, name="reading-status-view"),  # Add or update reading status
    path("reading-status/<int:pk>/", modify_reading_status, name="reading-status-detail"),  # Single book status



]
