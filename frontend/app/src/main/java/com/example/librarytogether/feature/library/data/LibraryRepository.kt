package com.example.librarytogether.feature.library.data

import android.content.Context
import android.util.Log
import androidx.core.content.ContentProviderCompat.requireContext
import com.example.librarytogether.network.RetrofitClient
import retrofit2.Response
import javax.inject.Inject
import javax.inject.Singleton

data class Review(
    val id: Int,
    val bookTitle: String,
    val authorName: String,
    val userName: String,
    val userProfile: String,
    val content: String,
    val imageUrls: List<String> = emptyList(),
    val likeCount: Int = 0,
    val createdAt: String? = null,
)

data class postReview(
    val bookTitle: String,
    val authorName: String,
    val content: String,
    val imageUrls: List<String> = emptyList(),
)

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
}