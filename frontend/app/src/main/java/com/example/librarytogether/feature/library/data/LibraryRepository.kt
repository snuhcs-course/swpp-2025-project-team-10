package com.example.librarytogether.feature.library.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LibraryRepository @Inject constructor(
    private val libraryApi: LibraryApi
) {
    suspend fun getMyReviews(): List<Review>? {
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

    suspend fun addReview(review: postReview) {
        try {
            libraryApi.addReview(review)
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error adding review", e)
        }
    }

    suspend fun toggleReviewLike(reviewId: Int): Review? {
        return try {
            val response = libraryApi.toggleReviewLike(reviewId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("LibraryRepository", "Like toggle failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("LibraryRepository", "Error toggling like", e)
            null
        }
    }

    suspend fun getMyBooks(): List<Book>? {
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

    suspend fun getMyProfile(): UserProfile? {
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

    suspend fun updateMyProfile(profile: UserProfile): UserProfile? {
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

    suspend fun getMyWishlist(): List<Book>? {
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
}
