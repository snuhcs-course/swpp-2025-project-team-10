package com.example.librarytogether.feature.barterapproval.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BarterApprovalRepository @Inject constructor(
    private val api: BarterApprovalApi
) {

    suspend fun getBarterApproval(id: String): BarterApprovalDetail {
        return try {
            val res = api.getBarterApproval(id)
            if (res.isSuccessful) {
                res.body() ?: throw IllegalStateException("Empty body for id=$id")
            } else {
                throw IllegalStateException("Failed to load barter approval: ${res.code()}")
            }
        } catch (e: Exception) {
            Log.e("BarterApprovalRepo", "Error fetching approval detail id=$id", e)
            throw e
        }
    }

    suspend fun acceptBook(requestId: String, bookId: String) {
        try {
            val res = api.acceptBook(requestId, bookId)
            if (!res.isSuccessful) {
                throw IllegalStateException("Failed to accept book $bookId for request $requestId")
            }
        } catch (e: Exception) {
            Log.e("BarterApprovalRepo", "Error accepting book $bookId (req=$requestId)", e)
            throw e
        }
    }

    suspend fun rejectRequest(requestId: String) {
        try {
            val res = api.rejectRequest(requestId)
            if (!res.isSuccessful) {
                throw IllegalStateException("Failed to reject request $requestId")
            }
        } catch (e: Exception) {
            Log.e("BarterApprovalRepo", "Error rejecting request $requestId", e)
            throw e
        }
    }
}
