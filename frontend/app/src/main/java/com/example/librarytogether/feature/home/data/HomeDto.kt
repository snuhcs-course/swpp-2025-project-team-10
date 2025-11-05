package com.example.librarytogether.feature.home.data

//data class ApiResponse<T>(
//    val success: Boolean,
//    val data: T? = null,
//    val message: String? = null,
//    val error: ApiError? = null,
//    val pagination: Pagination? = null
//)
//
//data class ApiError(
//    val code: String,
//    val message: String,
//    val details: Map<String, Any>? = null
//)
//
//data class Pagination(
//    val page: Int,
//    val size: Int,
//    val total: Int,
//    val total_pages: Int
//)

data class Post(
    val id: Int,
    val bookTitle: String,
    val authorName: String,
    val posterName: String,
    val posterProfile: String, // profile image
    val content: String,
    val imageUrls: List<String> = emptyList(),
    val likeCount: Int = 0,
    val createdAt: String? = null,
    val isLiked: Boolean = false,
    val userBookId: Int // 교환 대상 책 아이디
)

data class FeedResponse(
    val results: List<Post>
)

data class LikeResponse(
    val post: Post
)
