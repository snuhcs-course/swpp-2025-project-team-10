package com.example.librarytogether.feature.comment.data

import com.example.librarytogether.feature.home.data.Post
import javax.inject.Inject

class CommentRepository @Inject constructor(
    private val api: CommentApi
) {

    suspend fun writeComment(postId: Int, content: String): Post {
        val res = api.createComment(postId, CommentCreateDto(content))
        return res.post
    }

    suspend fun deleteComment(postId: Int, commentId: String): Post {
        val res = api.deleteComment(postId, commentId)
        return res.post
    }

    suspend fun editComment(postId: Int, commentId: String, content: String): Post {
        val res = api.editComment(postId, commentId, CommentCreateDto(content))
        return res.post
    }
    suspend fun toggleCommentLike(postId: Int, commentId: String): CommentDto {
        val res = api.toggleCommentLike(postId, commentId)
        return res.comment
    }
}
