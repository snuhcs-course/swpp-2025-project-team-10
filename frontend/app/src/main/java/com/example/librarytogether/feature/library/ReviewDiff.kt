package com.example.librarytogether.feature.library

import androidx.recyclerview.widget.DiffUtil
import com.example.librarytogether.feature.library.data.Review

object ReviewDiff : DiffUtil.ItemCallback<Review>() {
    override fun areItemsTheSame(oldItem: Review, newItem: Review): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Review, newItem: Review): Boolean =
        oldItem == newItem
}