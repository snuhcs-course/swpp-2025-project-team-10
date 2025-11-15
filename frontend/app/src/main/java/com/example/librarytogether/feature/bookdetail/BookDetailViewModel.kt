package com.example.librarytogether.feature.bookdetail

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.bookdetail.data.BookRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.launch

@HiltViewModel
class BookDetailViewModel @Inject constructor(
    private val repository: BookRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val bookId: String = checkNotNull(savedStateHandle["bookId"])

    private val _state = MutableLiveData<UiState>(UiState.Loading)
    val state: LiveData<UiState> = _state

    fun load() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            runCatching { repository.getBookDetail(bookId) }
                .onSuccess { detail -> _state.value = UiState.Data(detail) }
                .onFailure { e -> _state.value = UiState.Error(e.message ?: "error") }
        }
    }

    sealed class UiState {
        object Loading : UiState()
        data class Data(val book: BookDetail) : UiState()
        data class Error(val message: String) : UiState()
    }
}
