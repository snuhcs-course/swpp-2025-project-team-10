package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.CommentLikeResponse
// [수정] PostResponse 대신 Post를 import 해야 합니다.
import com.example.librarytogether.feature.home.data.Post
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface CommentApi {
    @POST("posts/{postId}/comments/")
    suspend fun createComment(
        @Path("postId") postId: Int,
        @Body body: CommentCreateDto
    ): Post

    @DELETE("posts/{postId}/comments/{commentId}/delete/")
    suspend fun deleteComment(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String
    ): Post

    @PUT("posts/{postId}/comments/{commentId}/edit/")
    suspend fun editComment(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String,
        @Body body: CommentCreateDto
    ): Post

    @POST("posts/{postId}/comments/{commentId}/like/")
    suspend fun toggleCommentLike(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String
    ): CommentLikeResponse
}
