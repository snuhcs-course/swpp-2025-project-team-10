package com.example.librarytogether.feature.library

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.postReview
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LibraryViewModel @Inject constructor(
    private val repository: LibraryRepository
) : ViewModel() {
    private val _myReviews = MutableLiveData<List<Review>>(emptyList())
    val myReviews: LiveData<List<Review>> = _myReviews
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    init {
        refreshMyReviews()
    }

    fun refreshMyReviews() {
        viewModelScope.launch {
            val list = repository.getMyReviews()
            _myReviews.postValue(list)
        }
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val reviews = repository.getMyReviews()
                if (reviews != null) {
                    _myReviews.value = reviews
                } else {
                    _error.value = "리뷰를 불러오는 데 실패했습니다."
                }
            } catch (e: Exception) {
                _error.value = "네트워크 오류가 발생했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun onErrorShown() {
        _error.value = null
    }

    fun addNewReview(review: postReview) {
        viewModelScope.launch {
            repository.addReview(review)
            refreshMyReviews()
        }
    }
}