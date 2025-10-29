"""
URL configuration for the social app.
"""

from django.urls import path

from social import views

urlpatterns = [
    path("home/", views.home_feed, name="home-feed"),
    path("posts/<uuid:post_id>/like/", views.like_post, name="like-post"),
    path("posts/create/", views.create_post, name="create-post"),
]
