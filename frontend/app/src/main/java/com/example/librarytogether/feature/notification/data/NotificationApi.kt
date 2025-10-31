package com.example.librarytogether.feature.notification.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.Path

interface NotificationApi {
    @GET("notifications/")
    suspend fun getNotifications(): Response<List<NotificationDto>>

    @PATCH("notifications/{id}/read/")
    suspend fun markAsRead(@Path("id") id: Int): Response<Unit>
}
