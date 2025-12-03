package com.example.librarytogether.feature.comment.data

data class CommentDto(
    val id: String,
    val authorName: String,
    val authorProfile: ProfileDto?,
    val content: String,
    val createdAt: String,
    val updatedAt: String
)

data class ProfileDto(
    val username: String,
    val profile_picture: String?
)

// 댓글 작성 요청 바디
data class CommentCreateDto(
    val content: String
)
