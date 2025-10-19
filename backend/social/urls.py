from django.urls import path
from .views import like_post, add_comment, create_post, list_posts, like_comment, list_comments

urlpatterns = [

    path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/like/', like_post, name='like-post'),
    
    path('posts/<uuid:post_id>/comments/add/', add_comment, name='add-comment'),
    path('posts/<uuid:post_id>/<uuid:comment_id>/like/', like_comment, name='like-comment'),
    path('posts/<uuid:post_id>/comments/', list_comments, name='list-comments'),
]