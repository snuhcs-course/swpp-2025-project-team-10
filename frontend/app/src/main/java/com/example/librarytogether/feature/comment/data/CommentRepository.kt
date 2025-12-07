package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.Post
import javax.inject.Inject

class CommentRepository @Inject constructor(
    private val api: CommentApi
) {
    suspend fun writeComment(postId: Int, content: String): Post {
        return api.createComment(postId, CommentCreateDto(content))
    }

    suspend fun deleteComment(postId: Int, commentId: String): Post {
        return api.deleteComment(postId, commentId)
    }

    suspend fun editComment(postId: Int, commentId: String, content: String): Post {
        return api.editComment(postId, commentId, CommentCreateDto(content))
    }

    suspend fun toggleCommentLike(postId: Int, commentId: String): CommentDto {
        val res = api.toggleCommentLike(postId, commentId)
        return res.comment
    }
}
