package com.example.librarytogether.feature.barter

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.barter.data.BarterDetailResponse
import com.example.librarytogether.feature.barter.data.BarterOfferRequest
import com.example.librarytogether.feature.barter.data.BarterRepository
import com.example.librarytogether.feature.library.data.Book
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class BarterDetailViewModel @Inject constructor(
    private val repository: BarterRepository
) : ViewModel() {

    private val _barterDetails = MutableLiveData<BarterDetailResponse?>()
    val barterDetails: LiveData<BarterDetailResponse?> = _barterDetails

    private val _selectedBook = MutableLiveData<Book?>()
    val selectedBook: LiveData<Book?> = _selectedBook

    private val _myBooks = MutableLiveData<List<Book>>(emptyList())
    val myBooks: LiveData<List<Book>> = _myBooks

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private var currentUserBookId: Int? = null

    private val _navigateToOfferComplete = MutableLiveData<Boolean>(false)
    val navigateToOfferComplete: LiveData<Boolean> = _navigateToOfferComplete
    fun loadDetails(userBookId: Int) {
        _isLoading.value = true
        currentUserBookId = userBookId
        viewModelScope.launch {
            try {
                _barterDetails.value = repository.getBarterDetails(userBookId)
            } catch (e: Exception) {
                _error.value = "데이터를 불러오는 데 실패했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    // '내 서재에서 선택' 시 호출
    fun selectBook(book: Book) {
        _selectedBook.value = book
    }

    fun submitOffer(message: String) {
        val offer = _barterDetails.value ?: return
        val book = _selectedBook.value ?: run {
            _error.value = "교환할 책을 선택해주세요."
            return@submitOffer
        }
        val targetBookId = currentUserBookId ?: run {
            _error.value = "교환할 책을 선택해주세요."
            return@submitOffer
        }

        _isLoading.value = true
        val request = BarterOfferRequest(
            userBookId = targetBookId,
            myBookId = book.id,
            message = message
        )

        viewModelScope.launch {
            val success = repository.submitOffer(request)
            if (success) {
                _navigateToOfferComplete.value = true
            } else {
                _error.value = "교환 신청에 실패했습니다."
            }
            _isLoading.value = false
        }
    }

    fun onNavigationComplete() {
        _navigateToOfferComplete.value = false
    }
}
