package com.example.librarytogether.feature.library

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.PostBook
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.feature.library.data.PostReview
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LibraryViewModel @Inject constructor(
    private val repository: LibraryRepository
) : ViewModel() {
    private val _myReviews = MutableLiveData<List<Review>>(emptyList())
    val myReviews: LiveData<List<Review>> = _myReviews
    private val _myBooks = MutableLiveData<List<Book>>(emptyList())
    val myBooks: LiveData<List<Book>> = _myBooks
    private val _userProfile = MutableLiveData<UserProfile?>()
    val userProfile: LiveData<UserProfile?> = _userProfile
    private val _myWishlist = MutableLiveData<List<Book>>(emptyList())
    val myWishlist: LiveData<List<Book>> = _myWishlist
    private val _searchResults = MutableLiveData<List<Book>>(emptyList())
    val searchResults: LiveData<List<Book>> = _searchResults
    private val _navigateToLibrary = MutableLiveData<Boolean>(false)
    val navigateToLibrary: LiveData<Boolean> = _navigateToLibrary

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    init {
        refreshMyReviews()
        refreshMyBooks()
        loadProfile()
        refreshWishlist()
    }

    fun refreshMyReviews() {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val reviews = repository.getMyReviews()
                _myReviews.value = reviews ?: emptyList()
            } catch (e: Exception) {
                _error.value = "네트워크 오류가 발생했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun refreshMyBooks() {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val books = repository.getMyBooks()
                _myBooks.value = books ?: emptyList()
            } catch (e: Exception) {
                _error.value = "책장 목록을 불러오는 데 실패했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun loadProfile() {
        viewModelScope.launch {
            _userProfile.value = repository.getMyProfile()
        }
    }

    fun refreshWishlist() {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val books = repository.getMyWishlist()
                _myWishlist.value = books ?: emptyList()
            } catch (e: Exception) {
                _error.value = "위시리스트를 불러오는 데 실패했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun onErrorShown() {
        _error.value = null
    }

    fun addNewReview(review: PostReview) {
        viewModelScope.launch {
            repository.addReview(review)
            refreshMyReviews()
        }
    }

    fun addNewBook(book: PostBook) {
        viewModelScope.launch {
            try {
                val success = repository.addBook(book) // 1. Repository 호출
                if (success) {
                    refreshMyBooks()
                    _navigateToLibrary.value = true
                } else {
                    _error.value = "책 추가에 실패했습니다."
                }
            } catch (e: Exception) {
                _error.value = "책 추가 중 오류가 발생했습니다."
            }
        }
    }

    fun searchBook(query: String) {
        viewModelScope.launch {
            try {
                _searchResults.value = repository.searchBooks(query) ?: emptyList()
            } catch (e: Exception) {
                _error.value = "검색 중 오류가 발생했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearSearch() {
        _searchResults.value = emptyList()
    }

    fun onBookAddedNavigationComplete() {
        _navigateToLibrary.value = false
    }

    fun toggleLike(review: Review) {
        viewModelScope.launch {
            val updatedReview = repository.toggleReviewLike(review.id)
            if (updatedReview != null) {
                val currentList = _myReviews.value?.toMutableList() ?: mutableListOf()
                val index = currentList.indexOfFirst { it.id == review.id }
                if (index != -1) {
                    currentList[index] = updatedReview
                    _myReviews.value = currentList
                    //refreshMyReviews()
                }
            } else {
                _error.value = "좋아요 처리에 실패했습니다."
            }
        }
    }

    fun saveProfile(newProfile: UserProfile) {
        viewModelScope.launch {
            try {
                val updatedProfile = repository.updateMyProfile(newProfile)
                _userProfile.value = updatedProfile
            } catch (e: Exception) {
                _error.value = "프로필 저장에 실패했습니다."
            }
        }
    }
}
