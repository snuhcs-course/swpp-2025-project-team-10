// CommentDto.kt

package com.example.librarytogether.feature.comment.data

import com.google.gson.annotations.SerializedName

data class CommentDto(
    @SerializedName("id") val id: String,

    @SerializedName("author_name", alternate = ["authorName", "username"])
    val authorName: String? = "Unknown",

    @SerializedName("author_profile", alternate = ["authorProfile", "profile"])
    val authorProfile: ProfileDto?,

    @SerializedName("content") val content: String,

    @SerializedName("created_at", alternate = ["createdAt"])
    val createdAt: String,

    @SerializedName("like_count", alternate = ["likeCount"])
    val likeCount: Int = 0,

    @SerializedName("is_liked", alternate = ["isLiked"])
    val isLiked: Boolean = false,

    @SerializedName("updated_at", alternate = ["updatedAt"])
    val updatedAt: String? = null,

)

data class ProfileDto(
    val id: Int? = null,
    val username: String,
    val email: String? = null,
    @SerializedName("profile_picture", alternate = ["profilePicture"])
    val profilePicture: String?
)

data class CommentCreateDto(
    val content: String
)
