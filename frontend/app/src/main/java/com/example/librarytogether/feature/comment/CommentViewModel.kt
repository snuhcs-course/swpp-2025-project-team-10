package com.example.librarytogether.feature.comment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.comment.data.CommentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CommentViewModel @Inject constructor(
    private val repo: CommentRepository
) : ViewModel() {

    private val _comments = MutableLiveData<List<CommentDto>>(emptyList())
    val comments: LiveData<List<CommentDto>> = _comments

    private var postId: Int = -1

    fun initialize(postId: Int, initialComments: List<CommentDto>) {
        if (this.postId != -1) return
        this.postId = postId
        _comments.value = initialComments
    }

    fun writeComment(content: String) {
        viewModelScope.launch {
            val updatedPost = repo.writeComment(postId, content)
            _comments.value = updatedPost.comments
        }
    }

    fun deleteComment(dto: CommentDto) {
        viewModelScope.launch {
            val updatedPost = repo.deleteComment(postId, dto.id)
            _comments.value = updatedPost.comments
        }
    }

    fun editComment(commentId: String, newContent: String) {
        viewModelScope.launch {
            val updatedPost = repo.editComment(postId, commentId, newContent)
            _comments.value = updatedPost.comments
        }
    }

    fun toggleLike(dto: CommentDto) {
        viewModelScope.launch {
            val updatedComment = repo.toggleCommentLike(postId, dto.id)

            _comments.value = _comments.value?.map {
                if (it.id == updatedComment.id) updatedComment else it
            }
        }
    }
}
