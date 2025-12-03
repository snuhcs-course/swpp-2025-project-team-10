package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.CommentLikeResponse
import com.example.librarytogether.feature.home.data.PostResponse
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface CommentApi {

    /**
     * 댓글 작성
     * POST /posts/{postId}/comments/
     * Body: { "content": "text" }
     * Response: { "post": Post }
     */
    @POST("posts/{postId}/comments/")
    suspend fun createComment(
        @Path("postId") postId: Int,
        @Body body: CommentCreateDto
    ): PostResponse

    /**
     * 댓글 삭제
     * DELETE /posts/{postId}/comments/{commentId}/delete/
     * Response: { "post": Post }
     */
    @DELETE("posts/{postId}/comments/{commentId}/delete/")
    suspend fun deleteComment(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String
    ): PostResponse

    /**
     * 댓글 수정
     * PUT /posts/{postId}/comments/{commentId}/edit/
     * Body: { "content": "text" }
     * Response: { "post": Post }
     */
    @PUT("posts/{postId}/comments/{commentId}/edit/")
    suspend fun editComment(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String,
        @Body body: CommentCreateDto
    ): PostResponse

    @POST("posts/{postId}/comments/{commentId}/like/")
    suspend fun toggleCommentLike(
        @Path("postId") postId: Int,
        @Path("commentId") commentId: String
    ): CommentLikeResponse

}
