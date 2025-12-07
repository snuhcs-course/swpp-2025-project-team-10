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

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    private var postId: Int = -1

    fun initialize(postId: Int, initialComments: List<CommentDto>) {
        if (this.postId == postId) return

        this.postId = postId
        _comments.value = initialComments
    }
    fun writeComment(content: String) {
        viewModelScope.launch {
            try {
                val newComments = repo.writeComment(postId, content)
                _comments.value = newComments
            } catch (e: Exception) {
                _error.value = "작성 실패"
                e.printStackTrace()
            }
        }
    }

    fun deleteComment(dto: CommentDto) {
        viewModelScope.launch {
            try {
                val newComments = repo.deleteComment(postId, dto.id)
                _comments.value = newComments
            } catch (e: Exception) {
                _error.value = "삭제 실패"
            }
        }
    }

    fun editComment(commentId: String, newContent: String) {
        viewModelScope.launch {
            try {
                val newComments = repo.editComment(postId, commentId, newContent)
                _comments.value = newComments
            } catch (e: Exception) {
                _error.value = "수정 실패"
            }
        }
    }

    fun toggleLike(dto: CommentDto) {
        viewModelScope.launch {
            val currentList = _comments.value.orEmpty().toMutableList()
            val index = currentList.indexOfFirst { it.id == dto.id }
            if (index != -1) {
                val old = currentList[index]
                val newState = !old.isLiked
                val newCount = if (newState) old.likeCount + 1 else old.likeCount - 1
                currentList[index] = old.copy(isLiked = newState, likeCount = newCount)
                _comments.value = currentList
            }
            try {
                repo.toggleCommentLike(postId, dto.id)
            } catch (e: Exception) {
                _error.value = "좋아요 실패"
            }
        }
    }
}
