package com.example.librarytogether.feature.notification.data

data class NotificationDto(
    val id: String,
    val title: String,
    val body: String,
    val created_at: String,
    val is_read: Boolean,
    val deepLink: String?,
    val type: String?
)

