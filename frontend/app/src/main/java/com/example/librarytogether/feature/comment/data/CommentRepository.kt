package com.example.librarytogether.feature.comment.data

import javax.inject.Inject

class CommentRepository @Inject constructor(
    private val api: CommentApi
) {

    suspend fun getComments(postId: Int): List<CommentDto> {
        return api.getComments(postId)
    }

    suspend fun writeComment(postId: Int, text: String) {
        api.createComment(postId, CommentCreateDto(text))
    }
}
