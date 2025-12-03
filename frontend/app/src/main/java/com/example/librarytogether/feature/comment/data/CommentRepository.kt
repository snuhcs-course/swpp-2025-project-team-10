package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.Post
import javax.inject.Inject

class CommentRepository @Inject constructor(
    private val api: CommentApi
) {

    /**
     * 댓글 작성
     * Response: 최신 Post
     */
    suspend fun writeComment(postId: Int, content: String): Post {
        val response = api.createComment(
            postId = postId,
            body = CommentCreateDto(content)
        )
        return response.post
    }

    /**
     * 댓글 삭제
     * Response: 최신 Post
     */
    suspend fun deleteComment(postId: Int, commentId: String): Post {
        val response = api.deleteComment(
            postId = postId,
            commentId = commentId
        )
        return response.post
    }

    /**
     * 댓글 수정
     * Response: 최신 Post
     */
    suspend fun editComment(postId: Int, commentId: String, content: String): Post {
        val response = api.editComment(
            postId = postId,
            commentId = commentId,
            body = CommentCreateDto(content)
        )
        return response.post
    }
}
