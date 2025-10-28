package com.example.librarytogether.feature.home.data

import android.content.Context
import android.util.Log
import androidx.core.content.ContentProviderCompat.requireContext
import com.example.librarytogether.feature.library.data.LibraryApi
import com.example.librarytogether.network.RetrofitClient
import retrofit2.Response
import javax.inject.Inject
import javax.inject.Singleton

data class Post(
    val id: Int,
    val bookTitle: String,
    val authorName: String,
    val posterName: String,
    val posterProfile: String,
    val content: String,
    val imageUrls: List<String> = emptyList(),
    val likeCount: Int = 0,
    val createdAt: String? = null,
    val isLiked: Boolean = false
)

@Singleton
class HomeRepository @Inject constructor(
    private val homeApi: HomeApi
) {
    suspend fun getFeed(): List<Post> {
        return try {
            val response = homeApi.feed()
            if (response.isSuccessful) {
                response.body()?.results ?: emptyList()
            } else {
                throw IllegalStateException("Failed to get feed: ${response.code()}")
            }
        } catch (e: Exception) {
            Log.e("HomeRepository", "Error fetching feed", e)
            throw e
        }
    }

    suspend fun toggleLike(postId: Int): Post {
        return try {
            val response = homeApi.togglePostLike(postId)
            if (response.isSuccessful) {
                response.body()?.post
                    ?: throw IllegalStateException("Response body is null")
            } else {
                throw IllegalStateException("Failed to toggle like: ${response.code()}")
            }
        } catch (e: Exception) {
            Log.e("HomeRepository", "Error toggling like", e)
            throw e
        }
    }
}
