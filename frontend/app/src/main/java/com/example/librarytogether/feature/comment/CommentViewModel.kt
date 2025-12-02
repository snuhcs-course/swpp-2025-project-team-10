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
    private val repository: CommentRepository
) : ViewModel() {

    private val _comments = MutableLiveData<List<CommentDto>>(emptyList())
    val comments: LiveData<List<CommentDto>> = _comments

    fun loadComments(postId: Int) {
        viewModelScope.launch {
            try {
                val list = repository.getComments(postId)
                _comments.value = list
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun addCommentLocal(content: String, author: String) {
        val current = _comments.value?.toMutableList() ?: mutableListOf()
        current.add(CommentDto(author, content, System.currentTimeMillis()))
        _comments.value = current
    }

    fun writeComment(postId: Int, content: String) {
        viewModelScope.launch {
            try {
                repository.writeComment(postId, content)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}
