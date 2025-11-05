package com.example.librarytogether.feature.explore

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ExploreViewModel @Inject constructor(
) : ViewModel() {

    private val _isLoading = MutableLiveData(true)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>(null)
    val error: LiveData<String?> = _error

    init {
        viewModelScope.launch {
            // TODO: repository.fetchExplore()
            _isLoading.value = true // demo
        }
    }

    fun onErrorShown() { _error.value = null }

    fun refresh() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // repository.fetchExplore()
            } catch (e: Exception) {
                _error.value = "탐색 데이터를 불러오지 못했어요."
            } finally {
                _isLoading.value = false
            }
        }
    }
}
