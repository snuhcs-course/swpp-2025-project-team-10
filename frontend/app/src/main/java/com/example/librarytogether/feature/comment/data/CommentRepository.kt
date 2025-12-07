package com.example.librarytogether.feature.comment.data

import javax.inject.Inject

class CommentRepository @Inject constructor(
    private val api: CommentApi
) {
    suspend fun writeComment(postId: Int, content: String): List<CommentDto> {
        val container = api.createComment(postId, CommentCreateDto(content))
        return container.post.comments ?: emptyList()
    }
    suspend fun deleteComment(postId: Int, commentId: String): List<CommentDto> {
        val container = api.deleteComment(postId, commentId)
        return container.post.comments ?: emptyList()
    }
    suspend fun editComment(postId: Int, commentId: String, content: String): List<CommentDto> {
        val container = api.editComment(postId, commentId, CommentCreateDto(content))
        return container.post.comments ?: emptyList()
    }
    suspend fun toggleCommentLike(postId: Int, commentId: String) {
        api.toggleCommentLike(postId, commentId)
    }
}
