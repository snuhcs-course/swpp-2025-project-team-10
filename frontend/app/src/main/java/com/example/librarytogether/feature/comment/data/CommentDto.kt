package com.example.librarytogether.feature.comment.data

data class CommentDto(
    val id: String,
    val authorName: String,
    val authorProfile: ProfileDto?,
    val content: String,
    val createdAt: String,
    val updatedAt: String,
    val like_count: Int,
    val isLiked: Boolean
)

data class ProfileDto(
    val username: String,
    val profile_picture: String?
)

data class CommentCreateDto(
    val content: String
)
