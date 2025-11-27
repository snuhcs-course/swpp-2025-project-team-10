package com.example.librarytogether.feature.home.data

import android.util.Log
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
open class HomeRepository @Inject constructor(
    private val homeApi: HomeApi
) {
    open suspend fun getFeed(): List<Post> {
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

    open suspend fun toggleLike(postId: Int): Post {
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


    open suspend fun createRequest(recipientId: Int, requestedBookId: String): Boolean {
        return try {
            val res = homeApi.createRequest(CreateBarterRequest(recipientId, requestedBookId))

            if (res.isSuccessful) {
                true
            } else {
                val raw = res.errorBody()?.string()
                val message = parseBarterErrorMessage(raw)
                throw IllegalStateException(message)
            }
        } catch (e: Exception) {
            Log.e("HomeRepository", "Error creating barter request", e)
            throw e
        }
    }

    private fun parseBarterErrorMessage(raw: String?): String {
        if (raw.isNullOrBlank()) {
            return "교환 신청에 실패했어요."
        }

        return try {
            val json = JSONObject(raw)

            val serverMessage = when {
                json.has("error") -> json.optString("error")
                else -> null
            }

            translateBarterError(serverMessage) ?: "교환 신청에 실패했어요."
        } catch (e: Exception) {
            "교환 신청에 실패했어요."
        }
    }

    private fun translateBarterError(serverMessage: String?): String? {
        return when (serverMessage) {
            "recipient_id is required" ->
                "수신자 정보가 올바르지 않아요."

            "Recipient user not found" ->
                "요청 대상 사용자를 찾을 수 없어요."

            "Requested book not found" ->
                "요청한 도서를 찾을 수 없어요."

            "Requested book must belong to recipient" ->
                "요청한 도서는 상대방의 책이어야 해요."

            "Requested book is not available for barter" ->
                "요청한 도서는 지금 교환 가능한 상태가 아니에요."

            "Cannot request your own book" ->
                "내 책에는 교환 신청을 보낼 수 없어요."

            "You need at least 1 book available for barter." ->
                "교환 가능한 책이 최소 1권 이상 있어야 해요."

            else -> null
        }
    }
}
