package com.example.librarytogether.feature.barterapproval

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalRepository
import com.example.librarytogether.feature.library.data.Book
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.launch

@HiltViewModel
class BarterApprovalViewModel @Inject constructor(
    private val repository: BarterApprovalRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val requestId: String = checkNotNull(savedStateHandle["requestId"])

    sealed class UiState {
        object Loading : UiState()
        data class Data(
            val detail: BarterApprovalDetail
        ) : UiState()
        data class Error(val message: String) : UiState()
    }

    private val _state = MutableLiveData<UiState>(UiState.Loading)
    val state: LiveData<UiState> = _state

    private val _selectedBook = MutableLiveData<Book?>(null)
    val selectedBook: LiveData<Book?> = _selectedBook

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            runCatching { repository.getBarterApproval(requestId) }
                .onSuccess { detail -> _state.value = UiState.Data(detail) }
                .onFailure { e ->
                    _state.value = UiState.Error(
                        e.message ?: "교환 요청 정보를 불러오지 못했습니다."
                    )
                }
        }
    }

    fun toggleSelectedBook(book: Book) {
        _selectedBook.value =
            if (_selectedBook.value?.id == book.id) null else book
    }

    fun acceptBook(book: Book) {
        viewModelScope.launch {
            val current = _state.value
            if (current !is UiState.Data) return@launch

            runCatching {
                repository.acceptBook(requestId, book.id)
            }.onSuccess {
                val updatedBooks = current.detail.books.filterNot { it.id == book.id }
                _state.value = UiState.Data(
                    current.detail.copy(books = updatedBooks)
                )
            }.onFailure { e ->
                _state.value = UiState.Error(
                    e.message ?: "교환 요청을 승인하지 못했습니다."
                )
            }
        }
    }

    fun rejectRequest(onDone: () -> Unit) {
        viewModelScope.launch {
            runCatching {
                repository.rejectRequest(requestId)
            }.onSuccess {
                onDone()
            }.onFailure { e ->
                _state.value = UiState.Error(
                    e.message ?: "교환 요청을 거절하지 못했습니다."
                )
            }
        }
    }
}
