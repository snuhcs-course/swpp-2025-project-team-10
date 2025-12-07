package com.example.librarytogether.feature.comment

import android.util.Log
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

    // error 발생 시 UI notice LiveData
    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    private var postId: Int = -1

    // [중요] 초기화 로직
    fun initialize(postId: Int, initialComments: List<CommentDto>) {
        if (this.postId != -1) return
        this.postId = postId

        // 백엔드에 조회 API가 없으므로, 넘겨받은 댓글을 즉시 화면에 보여줍니다.
        Log.d("CommentVM", "초기화 됨. 댓글 수: ${initialComments.size}")
        _comments.value = initialComments
    }

    // 2. 댓글 작성
    fun writeComment(content: String) {
        viewModelScope.launch {
            try {
                // 백엔드가 갱신된 Post 객체를 통째로 줍니다.
                Log.d("CommentVM", "댓글 작성 시도: $content")
                val updatedPost = repo.writeComment(postId, content)

                Log.d("CommentVM", "작성 성공! 응답 받은 댓글 수: ${updatedPost.comments?.size}")
                // Post 안에 있는 최신 댓글 목록으로 갱신.
                _comments.value = updatedPost.comments ?: emptyList()
            } catch (e: Exception) {
                // 에러 발생 시 로그캣에 빨간색으로 출력
                Log.e("CommentVM", "댓글 작성 실패", e)
                _error.value = "전송 실패: ${e.message}"            }
        }
    }

    // 3. 댓글 삭제 (요청하신 부분)
    fun deleteComment(dto: CommentDto) {
        viewModelScope.launch {
            try {
                // 삭제 후 갱신된 Post 객체를 받습니다.
                val updatedPost = repo.deleteComment(postId, dto.id)
                // 화면 갱신
                _comments.value = updatedPost.comments ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
                _error.value = "댓글 삭제 실패: ${e.message}"
            }
        }
    }
    // 4. 댓글 수정 (요청하신 부분)
    fun editComment(commentId: String, newContent: String) {
        viewModelScope.launch {
            try {
                // 수정 후 갱신된 Post 객체를 받습니다.
                val updatedPost = repo.editComment(postId, commentId, newContent)
                // 화면 갱신
                _comments.value = updatedPost.comments ?: emptyList()
            } catch (e: Exception) {
                e.printStackTrace()
                _error.value = "댓글 수정 실패: ${e.message}"
            }
        }
    }

    // 5. 좋아요 (이건 백엔드가 Post가 아니라 Comment 정보를 주기 때문에 로직이 조금 다릅니다)
    fun toggleLike(dto: CommentDto) {
        viewModelScope.launch {
            try {
                // 좋아요 토글 후 변경된 '댓글 하나'의 정보를 받습니다.
                val updatedComment = repo.toggleCommentLike(postId, dto.id)

                // 현재 리스트에서 해당 댓글만 찾아서 갈아끼웁니다.
                val currentList = _comments.value.orEmpty().toMutableList()
                val index = currentList.indexOfFirst { it.id == updatedComment.id }

                if (index != -1) {
                    currentList[index] = updatedComment
                    _comments.value = currentList
                }
            } catch (e: Exception) {
                e.printStackTrace()
                // 좋아요 실패는 보통 조용히 넘어가거나 토스트 메시지 정도만 띄웁니다.
            }
        }
    }
}
