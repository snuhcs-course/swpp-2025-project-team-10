package com.example.librarytogether.feature.notification

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.librarytogether.feature.notification.data.NotificationDto
import com.example.librarytogether.feature.notification.data.NotificationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class NotificationViewModel @Inject constructor(
    private val repo: NotificationRepository
) : ViewModel() {

    private val _items = MutableLiveData<List<NotificationDto>>(emptyList())
    val items: LiveData<List<NotificationDto>> = _items

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    fun load() {
        _loading.value = true
        viewModelScope.launch {
            val list = repo.fetchNotifications()
            _items.value = list
            _loading.value = false
        }
    }

    fun markAsRead(item: NotificationDto) {
        viewModelScope.launch {
            if (!item.isRead && repo.markAsRead(item.id)) {
                _items.value = _items.value?.map {
                    if (it.id == item.id) it.copy(isRead = true) else it
                }
            }
        }
    }
}

