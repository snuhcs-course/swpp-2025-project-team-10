package com.example.librarytogether.feature.search

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _results = MutableLiveData<List<SearchItem>>(emptyList())
    val results: LiveData<List<SearchItem>> = _results

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _isLoading = MutableLiveData<Boolean>(false)
    val isLoading: LiveData<Boolean> = _isLoading

    fun search(query: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val res = repository.search(query)
                _results.value = res
                _error.value = null
            } catch (e: Exception) {
                _results.value = emptyList()
                _error.value = "검색 중 오류가 발생했습니다. 다시 시도해주세요."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearSearch() {
        _results.value = emptyList()
    }

    fun onErrorShown() { _error.value = null }
}
