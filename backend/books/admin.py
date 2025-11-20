from django.contrib import admin

from .models import (
    Author,
    BookCollection,
    BookCopy,
    BookPublication,
    BookReview,
    BookWishlist,
    Genre,
    Publisher,
    ReadingStatus,
    Translator,
)

admin.site.register(BookPublication)
admin.site.register(BookCopy)
admin.site.register(BookReview)
admin.site.register(BookWishlist)
admin.site.register(BookCollection)
admin.site.register(ReadingStatus)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Translator)
admin.site.register(Publisher)
