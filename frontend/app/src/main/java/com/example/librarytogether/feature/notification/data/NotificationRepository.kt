package com.example.librarytogether.feature.notification.data

import android.util.Log
import javax.inject.Inject

class NotificationRepository @Inject constructor(
    private val api: NotificationApi
) {
    suspend fun fetchNotifications(): List<NotificationDto> {
        return try {
            val res = api.getNotifications()
            if (res.isSuccessful) res.body() ?: emptyList()
            else emptyList()
        } catch (e: Exception) {
            Log.e("NotificationRepository", "fetchNotifications error", e)
            emptyList()
        }
    }

    suspend fun markAsRead(id: String): Boolean {
        return try {
            val res = api.markAsRead(id)
            res.isSuccessful
        } catch (e: Exception) {
            Log.e("NotificationRepository", "markAsRead error", e)
            false
        }
    }
}
