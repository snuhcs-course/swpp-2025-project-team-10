package com.example.librarytogether.feature.notification.data

data class NotificationDto(
    val id: Int,
    val title: String,
    val body: String,
    val date: String,
    val is_read: Boolean,
    val deepLink: String?,
    val notification_type: String?
)

