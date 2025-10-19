from django.urls import path
from . import views

urlpatterns = [
    # Books
    path('', views.list_books, name='list_books'),
    path('add/', views.add_book, name='add_book'),
    path('detail/<str:title>/', views.book_detail_by_title, name='book_detail_by_title'),

    # Reviews (no book_id in URL now)
    path('reviews/', views.list_reviews, name='list_reviews'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/helpful/', views.mark_review_helpful, name='mark_review_helpful'),

    # Wishlist
    path('wishlist/', views.list_wishlist, name='list_wishlist'),
    path('wishlist/add/<str:title>/', views.add_to_wishlist_by_title, name='add_to_wishlist_by_title'),
]