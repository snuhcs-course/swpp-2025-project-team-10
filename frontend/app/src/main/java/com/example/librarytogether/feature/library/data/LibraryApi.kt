package com.example.librarytogether.feature.library.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface LibraryApi {
    @GET("library/reviews/")
    suspend fun getMyReviews(): Response<ReviewResponse>

    @POST("library/reviews/")
    suspend fun addReview(@Body review: PostReview): Response<Unit>

    @POST("library/reviews/{id}/like/")
    suspend fun toggleReviewLike(@Path("id") reviewId: Int): Response<Review>

    @GET("library/books/")
    suspend fun getMyBooks(): Response<List<Book>>

    @POST("library/books/")
    suspend fun addBook(@Body book: PostBook): Response<Unit>

    /**
     * 'AddBookFragment'의 'searchBook'이 호출할 API
     * (ex: /books/search/?query=harrypoter)
     */
    @GET("books/search/")
    suspend fun searchBooks(@Query("query") query: String): Response<List<Book>>

    @GET("accounts/profile/me/")
    suspend fun getMyProfile(): Response<UserProfile>

    @PATCH("accounts/profile/me/")
    suspend fun updateMyProfile(@Body profile: UserProfile): Response<UserProfile>

    @GET("library/wishlist/")
    suspend fun getMyWishlist(): Response<List<Book>>
}
