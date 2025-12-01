package com.example.librarytogether.feature.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.profile.data.ProfileRepository
import com.example.librarytogether.feature.profile.data.UserProfile
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository
) : ViewModel() {

    private val _userId = MutableLiveData<Int>()
    val userId: LiveData<Int> = _userId

    private val _userProfile = MutableLiveData<UserProfile?>()
    val userProfile: LiveData<UserProfile?> = _userProfile

    private val _books = MutableLiveData<List<Book>>(emptyList())
    val books: LiveData<List<Book>> = _books

    private val _reviews = MutableLiveData<List<Review>>(emptyList())
    val reviews: LiveData<List<Review>> = _reviews

    private val _wishlist = MutableLiveData<List<Book>>(emptyList())
    val wishlist: LiveData<List<Book>> = _wishlist

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    private val _followLoading = MutableLiveData(false)
    val followLoading: LiveData<Boolean> = _followLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadUserProfile(userId: Int) {
        if (_userId.value == userId) return

        _userId.value = userId
        _loading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                _userProfile.value = repository.getUserProfile(userId)
                _books.value = this@ProfileViewModel.repository.getUserBooks(userId).orEmpty()
                _reviews.value = this@ProfileViewModel.repository.getUserReviews(userId).orEmpty()
                _wishlist.value = this@ProfileViewModel.repository.getUserWishlist(userId).orEmpty()
            } catch (e: Exception) {
                _error.value = e.message ?: "프로필을 불러오지 못했습니다."
            } finally {
                _loading.value = false
            }
        }
    }

    fun refreshBooks() = withUserId {
        _loading.value = true
        viewModelScope.launch {
            try {
                _books.value = this@ProfileViewModel.repository.getUserBooks(it).orEmpty()
            } catch (_: Exception) {
                _error.value = "책장을 불러오는 데 실패했습니다."
            } finally {
                _loading.value = false
            }
        }
    }

    fun refreshReviews() = withUserId {
        _loading.value = true
        viewModelScope.launch {
            try {
                _reviews.value = this@ProfileViewModel.repository.getUserReviews(it).orEmpty()
            } catch (_: Exception) {
                _error.value = "리뷰를 불러오는 데 실패했습니다."
            } finally {
                _loading.value = false
            }
        }
    }

    fun refreshWishlist() = withUserId {
        _loading.value = true
        viewModelScope.launch {
            try {
                _wishlist.value = this@ProfileViewModel.repository.getUserWishlist(it).orEmpty()
            } catch (_: Exception) {
                _error.value = "위시리스트를 불러오는 데 실패했습니다."
            } finally {
                _loading.value = false
            }
        }
    }


    fun toggleFollow() = withUserId {
        val curr = _userProfile.value ?: return@withUserId
        _followLoading.value = true

        val targetIsFollowing = !curr.isFollowing
        val newFollowerCount = if (targetIsFollowing) curr.followerCount + 1 else curr.followerCount - 1

        _userProfile.value = curr.copy(
            isFollowing = targetIsFollowing,
            followerCount = newFollowerCount
        )

        viewModelScope.launch {
            val success = try {
                if (targetIsFollowing) {
                    repository.follow(it)
                } else {
                    repository.unfollow(it)
                }
            } catch (_: Exception) {
                false
            }

            if (!success) {
                _userProfile.value = curr
                _error.value = "팔로우 처리에 실패했습니다."
            }

            _followLoading.value = false
        }
    }

    fun toggleLike(reviewId: Int) {
        viewModelScope.launch {
            val updated = try {
                repository.toggleReviewLike(reviewId)
            } catch (_: Exception) { null }

            if (updated != null) {
                val old = _reviews.value.orEmpty()
                _reviews.value = old.map { if (it.id == reviewId) updated else it }
            } else {
                _error.value = "좋아요 처리에 실패했습니다."
            }
        }
    }

//    fun consumeError() { _error.value = null }

    private inline fun withUserId(block: (Int) -> Unit) {
        val id = _userId.value
        if (id == null) {
            _error.value = "유저 정보가 없습니다."
            return
        }
        block(id)
    }
}
