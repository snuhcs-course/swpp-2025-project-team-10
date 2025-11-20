from django.contrib import admin

from .models import (
    BookClub,
    BookClubMembership,
    Comment,
    CommentLike,
    Post,
    PostLike,
)

admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(BookClub)
admin.site.register(BookClubMembership)
