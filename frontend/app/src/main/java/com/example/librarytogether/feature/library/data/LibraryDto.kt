package com.example.librarytogether.feature.library.data

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


data class Review(
    val id: Int,
    val bookTitle: String,
    val authorName: String,
    val userName: String,
    val userProfile: String, // profile image
    val content: String,
    val imageUrls: List<String> = emptyList(),
    val likeCount: Int = 0,
    val createdAt: String? = null,
    val isLiked: Boolean = false,
)

data class PostReview(
    val bookTitle: String,
    val authorName: String,
    val content: String,
    val publisher: String?,
    val isbn: String?,
    val imageUrls: List<String> = emptyList(),
)

data class Book(
    val id: String,
    val title: String,
    val authors: String?,
    val cover_image: String?,
    val publisher: String?,
    val isbn: String?
)

data class PostBook(
    val title: String,
    val authors: String,
    val publisher: String?,
    val isbn: String?,
    val is_for_barter: Boolean,
    val cover_image: String? = null
)

data class UserProfile(
    val username: String,
    val bio: String?,
    val profileUrl: String?,
    val reviewCount: Int = 0,
    val followerCount: Int = 0,
    val followingCount: Int = 0,
    val favoriteGenres: List<String>,
    val preferences: UserPreferences
)

data class UserPreferences(
    val tradeLocation1: String?,
    val tradeLocation2: String?,
    val tradeSpot1: String?,
    val tradeSpot2: String?,
    val favBook: String?,
    val favBookNote: String?,
    val favAuthor: String?,
    val favAuthorNote: String?,
    val readingHabit: String?
)

data class WishlistRequest(val book: PostBook)

data class ReviewResponse(
    val results: List<Review>
)

data class ReviewLikeResponse(
    val review: Review
)
