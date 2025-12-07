package com.example.librarytogether.feature.comment.data

import com.google.gson.annotations.SerializedName

data class CommentDto(
    @SerializedName("id") val id: String,

    // [중요] 백엔드는 보통 'author' 객체 안에 username을 담거나,
    // Serializer에서 'author_name'으로 보낼 수 있습니다.
    // 백엔드 PostSerializer 형식을 볼 때 camelCase로 변환 안 된 부분들이 있을 겁니다.
    // 안전하게 매핑합니다.
    @SerializedName("author_name", alternate = ["authorName", "username"])
    val authorName: String? = "Unknown", // null 방지용 기본값

    @SerializedName("author_profile", alternate = ["authorProfile", "profile"])
    val authorProfile: ProfileDto?,

    @SerializedName("content") val content: String,

    // [중요] Django는 created_at (snake_case)
    @SerializedName("created_at", alternate = ["createdAt"])
    val createdAt: String,

    @SerializedName("updated_at", alternate = ["updatedAt"])
    val updatedAt: String?,

    @SerializedName("like_count", alternate = ["likeCount"])
    val likeCount: Int = 0,

    @SerializedName("is_liked", alternate = ["isLiked"])
    val isLiked: Boolean = false
)

data class ProfileDto(
    val username: String,

    @SerializedName("profile_picture", alternate = ["profilePicture"])
    val profilePicture: String?
)

data class CommentCreateDto(
    val content: String
)
