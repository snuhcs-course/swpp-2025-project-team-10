package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.LikeResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface CommentApi {

    // 댓글 목록 불러오기 (GET)
    @GET("posts/{postId}/comments/")
    suspend fun getComments(
        @Path("postId") postId: Int
    ): List<CommentDto>

    // 댓글 작성 (POST)
    @POST("posts/{postId}/comments/")
    suspend fun createComment(
        @Path("postId") postId: Int,
        @Body body: CommentCreateDto
    ): Response<LikeResponse>
}

