"""
URL configuration for the social app.
"""

from django.urls import path
from social import views

urlpatterns = [
    path("home/", views.home_feed, name="home-feed"),
    path("posts/<int:post_id>/like/", views.like_post, name="like-post"),
    
    path("posts/<int:post_id>/barter/", views.barter_post, name="barter-post"),
    path(
        "posts/<int:post_id>/wishlist/",
        views.wishlist_post,
        name="wishlist-post",
    ),
    path("posts/create/", views.create_post, name="create-post"),
    path("posts/<int:post_id>/edit/", views.edit_post, name="edit-post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete-post"),

    path("posts/<int:post_id>/comments/", views.comment_post, name="comment-post"),
    path("posts/<int:post_id>/comments/<uuid:comment_id>/delete/", views.comment_delete, name="comment-delete"),

    path("posts/<int:post_id>/comments/<uuid:comment_id>/edit/", views.comment_edit, name="comment-edit"),  
]
