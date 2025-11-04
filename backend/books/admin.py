from django.contrib import admin
from .models import Book, BookReview, BookWishlist, BookCollection, ReadingStatus, Genre, Author, Publisher

admin.site.register(Book)
admin.site.register(BookReview)
admin.site.register(BookWishlist)
admin.site.register(BookCollection)
admin.site.register(ReadingStatus)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Publisher)
