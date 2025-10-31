package com.example.librarytogether.feature.notification.data

data class NotificationDto(
    val id: Int,
    val title: String,
    val body: String,
    val createdAt: String,
    val isRead: Boolean,
    val deepLink: String?,
    val type: String?
)

