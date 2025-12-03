package com.example.librarytogether.feature.comment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.comment.data.CommentRepository
import com.example.librarytogether.feature.home.data.Post
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CommentViewModel @Inject constructor(
    private val repository: CommentRepository
) : ViewModel() {

    private var postId: Int = -1

    private val _comments = MutableLiveData<List<CommentDto>>(emptyList())
    val comments: LiveData<List<CommentDto>> get() = _comments

    // 전체 Post를 보관 → 필요할 수 있어서 저장함
    private var currentPost: Post? = null


    /**
     * BottomSheet에서 최초 전달받은 Post로 초기화
     */
    fun initialize(post: Post) {
        postId = post.id
        currentPost = post

        // 초기 댓글 리스트 설정
        _comments.value = post.comments
    }


    /**
     * 댓글 작성
     */
    fun writeComment(content: String) {
        viewModelScope.launch {
            try {
                val updatedPost = repository.writeComment(postId, content)
                currentPost = updatedPost
                _comments.value = updatedPost.comments
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }


    /**
     * 댓글 삭제
     */
    fun deleteComment(comment: CommentDto) {
        viewModelScope.launch {
            try {
                val updatedPost = repository.deleteComment(
                    postId = postId,
                    commentId = comment.id
                )
                currentPost = updatedPost
                _comments.value = updatedPost.comments
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }


    /**
     * 댓글 수정
     */
    fun editComment(commentId: String, newContent: String) {
        viewModelScope.launch {
            try {
                val updatedPost = repository.editComment(
                    postId = postId,
                    commentId = commentId,
                    content = newContent
                )
                currentPost = updatedPost
                _comments.value = updatedPost.comments
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}
