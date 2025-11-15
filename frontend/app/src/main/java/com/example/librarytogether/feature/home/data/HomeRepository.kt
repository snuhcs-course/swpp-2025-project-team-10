package com.example.librarytogether.feature.home.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

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

    suspend fun createRequest(recipientId: Int, requestedBookId: String): Boolean {
        val res = homeApi.createRequest(CreateBarterRequest(recipientId, requestedBookId))
        return res.isSuccessful
    }
}
