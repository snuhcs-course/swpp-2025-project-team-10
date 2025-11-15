package com.example.librarytogether.feature.profile.data

import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import retrofit2.Response
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ProfileApi {
    @GET("library/reviews/{userId}/")
    suspend fun getUserReviews(@Path("userId") userId: Int): Response<List<Review>>

    @GET("library/profile/{userId}/")
    suspend fun getUserProfile(@Path("userId") userId: Int): Response<UserProfile>

    @GET("library/books/{userId}/")
    suspend fun getUserBooks(@Path("userId") userId: Int): Response<List<Book>>

    @GET("library/wishlist/{userId}/")
    suspend fun getUserWishlist(@Path("userId") userId: Int): Response<List<Book>>

    @POST("users/follow/{userId}/")
    suspend fun follow(@Path("userId") userId: Int): Response<Unit>

    @DELETE("users/follow/{userId}/")
    suspend fun unfollow(@Path("userId") userId: Int): Response<Unit>

    @POST("library/reviews/{id}/like/")
    suspend fun toggleReviewLike(@Path("id") reviewId: Int): Response<Review>
}
