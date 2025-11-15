package com.example.librarytogether.feature.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.Post
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class SortType { LATEST, POPULAR }

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: HomeRepository
) : ViewModel() {
    private var originalPosts: List<Post> = emptyList()
    private val _posts = MutableLiveData<List<Post>>(emptyList())
    val posts: LiveData<List<Post>> = _posts

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _barterLoading = MutableLiveData(false)
    val barterLoading: LiveData<Boolean> = _barterLoading

    private val _barterSuccess = MutableLiveData<Boolean?>()
    val barterSuccess: LiveData<Boolean?> = _barterSuccess

    private val _barterError = MutableLiveData<String?>()
    val barterError: LiveData<String?> = _barterError

    init {
        loadFeed()
    }

    fun loadFeed() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val feedPosts = repository.getFeed()
                originalPosts = feedPosts
                applySort(SortType.LATEST)
            } catch (e: Exception) {
                _error.value = "네트워크 오류가 발생했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun applySort(type: SortType) {
        val sorted = when (type) {
            SortType.LATEST -> originalPosts.sortedByDescending { it.createdAt }
            SortType.POPULAR -> originalPosts.sortedByDescending { it.likeCount }
        }
        _posts.value = sorted.toList()
    }

    fun toggleLike(post: Post) {
        viewModelScope.launch {
            try{
                val updated = repository.toggleLike(post.id)
                applyLocalUpdate(updated)
            }
            catch (e: Exception) {
                _error.value = "좋아요를 토글하는 데 실패했습니다."
            }
        }
    }

    private fun applyLocalUpdate(updated: Post) {
        originalPosts = originalPosts.map { if (it.id == updated.id) updated else it }
        _posts.value = _posts.value?.map { if (it.id == updated.id) updated else it }
    }

    fun requestBarter(ownerId: Int, bookId: String) {
        _barterError.value = null
        viewModelScope.launch {
            try {
                val ok = repository.createRequest(
                    ownerId, requestedBookId = bookId
                )
                _barterSuccess.value = ok
                if (!ok) _barterError.value = "교환 신청에 실패했습니다."
            } catch (e: Exception) {
                _barterError.value = e.message ?: "네트워크 오류가 발생했습니다."
            } finally {
                _barterLoading.value = false
            }
        }
    }

    fun clearBarterResult() {
        _barterSuccess.value = null
        _barterError.value = null
    }

    fun onClickAdd(post: Post) {

    }

    fun addPost(post: Post) {
        viewModelScope.launch {
        }
    }

    fun onErrorShown() {
        _error.value = null
    }
}
