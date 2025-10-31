package com.example.librarytogether.feature.notification


import androidx.recyclerview.widget.DiffUtil
import com.example.librarytogether.feature.notification.data.NotificationDto

class NotificationDiff : DiffUtil.ItemCallback<NotificationDto>() {
    override fun areItemsTheSame(oldItem: NotificationDto, newItem: NotificationDto) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: NotificationDto, newItem: NotificationDto) =
        oldItem == newItem
}
