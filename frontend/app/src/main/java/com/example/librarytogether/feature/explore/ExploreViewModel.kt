package com.example.librarytogether.feature.explore

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.explore.data.ExploreRepository
import com.example.librarytogether.feature.library.data.Book
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ExploreViewModel @Inject constructor(
    private val repository: ExploreRepository
) : ViewModel() {
    private val _state = MutableLiveData<ExploreUi>(ExploreUi.Loading)
    val state: LiveData<ExploreUi> = _state

    fun loadRecommendations() = viewModelScope.launch {
        _state.value = ExploreUi.Loading
        runCatching { repository.getRecommendations() }
            .onSuccess { list ->
                _state.value = when {
                    list.isEmpty() -> ExploreUi.Empty
                    else -> ExploreUi.Data(list)
                }
            }
            .onFailure { e ->
                _state.value = ExploreUi.Error(e.message ?: "error")
            }
    }

}

sealed class ExploreUi {
    object Loading : ExploreUi()
    object Empty : ExploreUi()
    data class Data(val items: List<Book>) : ExploreUi()
    data class Error(val message: String) : ExploreUi()
}
