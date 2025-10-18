package com.example.librarytogether.feature.home.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface HomeApi {
    @GET("home/")
    suspend fun feed(): Response<FeedResponse>

    @POST("posts/{postId}/like/")
    suspend fun likePost(@Path("postId") postId: Int): Response<LikeResponse>
}
