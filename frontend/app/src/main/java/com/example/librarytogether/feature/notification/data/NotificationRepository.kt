package com.example.librarytogether.feature.notification.data

import android.util.Log
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalApi
import javax.inject.Inject

class NotificationRepository @Inject constructor(
    private val notificationApi: NotificationApi,
    private val barterApprovalApi: BarterApprovalApi
) {
    suspend fun fetchNotifications(): List<NotificationDto> {
        return try {
            val res = notificationApi.getNotifications()
            if (res.isSuccessful) res.body() ?: emptyList()
            else emptyList()
        } catch (e: Exception) {
            Log.e("NotificationRepository", "fetchNotifications error", e)
            emptyList()
        }
    }

    suspend fun markAsRead(id: String): Boolean {
        return try {
            val res = notificationApi.markAsRead(id)
            res.isSuccessful
        } catch (e: Exception) {
            Log.e("NotificationRepository", "markAsRead error", e)
            false
        }
    }

    suspend fun cancelBarter(requestId: String): Boolean {
        return try {
            val res = barterApprovalApi.rejectRequest(requestId)
            res.isSuccessful
        } catch (e: Exception) {
            Log.e("NotificationRepository", "cancelBarter error", e)
            false
        }
    }
}
