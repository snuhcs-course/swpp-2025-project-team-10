package com.example.librarytogether.feature.library

import androidx.recyclerview.widget.DiffUtil
import com.example.librarytogether.feature.library.data.Book

object BookDiff : DiffUtil.ItemCallback<Book>() {
    override fun areItemsTheSame(oldItem: Book, newItem: Book): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Book, newItem: Book): Boolean =
        oldItem == newItem
}
