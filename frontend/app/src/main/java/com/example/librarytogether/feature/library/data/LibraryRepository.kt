package com.example.librarytogether.feature.library.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
open class LibraryRepository @Inject constructor(
    private val libraryApi: LibraryApi
) {
    open suspend fun getMyReviews(): List<Review>? {
        return try {
            val response = libraryApi.getMyReviews()
            if (response.isSuccessful) {
                response.body()?.results
            } else {
                Log.e("LibraryRepository", "Response not successful: ${response.code()}")
                emptyList<Review>()
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error fetching my reviews", e)
            emptyList<Review>()
        }
    }

    open suspend fun addReview(review: PostReview) {
        try {
            libraryApi.addReview(review)
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error adding review", e)
        }
    }

    open suspend fun updateReview(reviewId: Int, review: PostReview) {
        try {
            libraryApi.updateReview(reviewId, review)
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error updating review", e)
        }
    }

    open suspend fun deleteReview(reviewId: Int){
        try {
            libraryApi.deleteReview(reviewId)
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error deleting review", e)
        }
    }

    open suspend fun toggleLike(reviewId: Int): Review {
        return try {
            val response = libraryApi.toggleReviewLike(reviewId)
            if (response.isSuccessful) {
                response.body()?.review ?: throw IllegalStateException("Response body is null")
            } else {
                throw IllegalStateException("Failed to toggle like: ${response.code()}")
            }
        } catch (e: Exception) {
            throw IllegalStateException("Error toggling like", e)
        }
    }

    open suspend fun getMyBooks(): List<Book>? {
        return try {
            val response = libraryApi.getMyBooks()
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("LibraryRepository", "getMyBooks failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error fetching my books", e)
            emptyList()
        }
    }

    open suspend fun addBook(book: PostBook): Boolean {
        return try {
            val response = libraryApi.addBook(book)
            if (!response.isSuccessful) {
                Log.e("LibraryRepository", "addBook failed: ${response.code()}")
            }
            response.isSuccessful
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error adding book", e)
            false
        }
    }

    open suspend fun searchBooks(query: String): List<Book>? {
        return try {
            val response = libraryApi.searchBooks(query) // Api 호출
            if (response.isSuccessful) {
                val body = response.body()
                Log.d("LibraryRepository", "Response body: $body")
                body
            } else {
                Log.e("LibraryRepository", "searchBooks failed: ${response.code()}")
                Log.e("LibraryRepository", "searchBooks failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error searching books", e)
            emptyList()
        }
    }

    open suspend fun getMyProfile(): UserProfile? {
        return try {
            val response = libraryApi.getMyProfile()
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("LibraryRepository", "getMyProfile failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error fetching my profile", e)
            null
        }
    }

    open suspend fun updateMyProfile(profile: UserProfile): UserProfile? {
        return try {
            val response = libraryApi.updateMyProfile(profile)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("LibraryRepository", "updatdMyProfile failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error updating my profile", e)
            null
        }
    }

    open suspend fun getMyWishlist(): List<Book>? {
        return try {
            val response = libraryApi.getMyWishlist()
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("LibraryRepository", "getMyWishlist failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error fetching my wishlist", e)
            emptyList()
        }
    }

    open suspend fun addToWishlistById(bookId: String): Boolean {
        return try {
            val res = libraryApi.addToWishlistById(bookId)
            if (!res.isSuccessful) Log.e("LibraryRepository", "addToWishlistById failed: ${res.code()}")
            res.isSuccessful
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error addToWishlistById", e)
            false
        }
    }

    open suspend fun removeFromWishlistById(bookId: String): Boolean {
        return try {
            val res = libraryApi.removeFromWishlistById(bookId)
            if (!res.isSuccessful) Log.e("LibraryRepository", "removeFromWishlistById failed: ${res.code()}")
            res.isSuccessful
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error removeFromWishlistById", e)
            false
        }
    }
}
