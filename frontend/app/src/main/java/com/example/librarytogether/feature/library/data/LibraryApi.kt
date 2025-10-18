package com.example.librarytogether.feature.library.data

import com.example.librarytogether.feature.home.data.FeedResponse
import com.example.librarytogether.feature.library.data.Review
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface LibraryApi {
    @GET("library/reviews/")
    suspend fun getMyReviews(): Response<ReviewResponse>

    @POST("library/reviews/")
    suspend fun addReview(@Body review: postReview): Response<Unit>
}
