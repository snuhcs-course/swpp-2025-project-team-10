package com.example.librarytogether.feature.bookdetail

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalRepository
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.bookdetail.data.BookRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.launch

@HiltViewModel
class BookDetailViewModel @Inject constructor(
    private val bookRepository: BookRepository,
    private val barterApprovalRepository: BarterApprovalRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val bookId: String = checkNotNull(savedStateHandle["bookId"])
    private val barterRequestId: String? = savedStateHandle["barterRequestId"]

    private val _state = MutableLiveData<UiState>(UiState.Loading)
    val state: LiveData<UiState> = _state
    private val _acceptState = MutableLiveData<AcceptState>(AcceptState.Idle)
    val acceptState: LiveData<AcceptState> = _acceptState

    fun load() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            runCatching { bookRepository.getBookDetail(bookId) }
                .onSuccess { detail -> _state.value = UiState.Data(detail) }
                .onFailure { e -> _state.value = UiState.Error(e.message ?: "error") }
        }
    }

    fun acceptSelectedBook() {
        val requestId = barterRequestId ?: return

        viewModelScope.launch {
            _acceptState.value = AcceptState.Loading
            runCatching {
                barterApprovalRepository.acceptBook(requestId, bookId)
            }.onSuccess {
                _acceptState.value = AcceptState.Success
            }.onFailure { e ->
                _acceptState.value = AcceptState.Error(
                    e.message ?: "알 수 없는 오류가 발생했습니다."
                )
            }
        }
    }

    sealed class UiState {
        object Loading : UiState()
        data class Data(val book: BookDetail) : UiState()
        data class Error(val message: String) : UiState()
    }

    sealed class AcceptState {
        object Idle : AcceptState()
        object Loading : AcceptState()
        object Success : AcceptState()
        data class Error(val message: String) : AcceptState()
    }
}
