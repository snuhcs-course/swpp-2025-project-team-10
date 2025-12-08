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
    val bookId: String? = null,
)

data class PostReview(
    val bookTitle: String,
    val authorName: String,
    val content: String,
    val publisher: String?,
    val isbn: String?,
    val imageUrls: List<String> = emptyList(),
    val bookId: String? = null,
)

data class Book(
    val id: String,
    val title: String,
    val authors: List<String>?,
    val cover_image: String?,
    val publisher: String?,
    val isbn: String?,
    val publicationId: String?
)
data class PostBook(
    val publication: String? = null,
    // Fields for existing publication (read-only on backend)
    val title: String? = null,
    val authors: String? = null,
    val publisher: String? = null,
    val isbn: String? = null,
    // Fields for creating new publication
    val book_title: String? = null,
    val book_authors: List<String>? = null,
    val book_publisher: String? = null,
    val book_isbn_10: String? = null,
    val book_isbn_13: String? = null,
    val book_published_date: String? = null,
    val book_description: String? = null,
    // Common fields
    val is_for_barter: Boolean = false,
    val owner_notes: String? = null
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
    val favBooks: List<String>?,
    val favBookNotes: List<String>?,
    val favAuthors: List<String>?,
    val favAuthorNotes: List<String>?,
    val readingHabit: String?,
)

data class WishlistRequest(val book: PostBook)

data class ReviewResponse(
    val results: List<Review>
)

data class ReviewLikeResponse(
    val review: Review
)
