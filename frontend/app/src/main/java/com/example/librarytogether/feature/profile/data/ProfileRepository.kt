package com.example.librarytogether.feature.profile.data

import android.util.Log
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
open class ProfileRepository @Inject constructor(
    private val profileApi: ProfileApi
) {

    open suspend fun getUserProfile(userId: Int): UserProfile? {
        return try {
            val response = profileApi.getUserProfile(userId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("ProfileRepository", "getUserProfile failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error fetching user profile", e)
            null
        }
    }

    open suspend fun getUserBooks(userId: Int): List<Book>? {
        return try {
            val response = profileApi.getUserBooks(userId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("ProfileRepository", "getUserBooks failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error fetching user books", e)
            emptyList()
        }
    }

    open suspend fun getUserReviews(userId: Int): List<Review>? {
        return try {
            val response = profileApi.getUserReviews(userId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("ProfileRepository", "getUserReviews failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error fetching user reviews", e)
            emptyList()
        }
    }

    open suspend fun getUserWishlist(userId: Int): List<Book>? {
        return try {
            val response = profileApi.getUserWishlist(userId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("ProfileRepository", "getUserWishlist failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error fetching user wishlist", e)
            emptyList()
        }
    }

    open suspend fun follow(userId: Int): Boolean {
        return try {
            val response = profileApi.follow(userId)
            if (!response.isSuccessful) {
                Log.e("ProfileRepository", "follow failed: ${response.code()}")
            }
            response.isSuccessful
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error follow", e)
            false
        }
    }

    open suspend fun unfollow(userId: Int): Boolean {
        return try {
            val response = profileApi.unfollow(userId)
            if (!response.isSuccessful) {
                Log.e("ProfileRepository", "unfollow failed: ${response.code()}")
            }
            response.isSuccessful
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error unfollow", e)
            false
        }
    }

    open suspend fun toggleReviewLike(reviewId: Int): Review? {
        return try {
            val response = profileApi.toggleReviewLike(reviewId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("ProfileRepository", "Like toggle failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("ProfileRepository", "Error toggling like", e)
            null
        }
    }
}
