package com.example.librarytogether.feature.comment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class CommentViewModel : ViewModel() {

    private val _comments = MutableLiveData<List<String>>(emptyList())
    val comments: LiveData<List<String>> = _comments

    fun addComment(text: String) {
        val current = _comments.value?.toMutableList() ?: mutableListOf()
        current.add(text)
        _comments.value = current
    }
}
