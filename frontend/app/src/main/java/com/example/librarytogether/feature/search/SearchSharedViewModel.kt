package com.example.librarytogether.feature.search

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class SearchSharedViewModel @Inject constructor() : ViewModel() {
    private val _pendingQuery = MutableLiveData<String?>()
    val pendingQuery: LiveData<String?> = _pendingQuery

    fun setQuery(query: String) {
        _pendingQuery.value = query
    }

    fun clearQuery() {
        _pendingQuery.value = null
    }
}

