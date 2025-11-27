package com.example.librarytogether.feature.library

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.databinding.ItemBookRowBinding
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.util.loadCover

class SearchBookAdapter(
    private val onClickItem: (Book) -> Unit
) : ListAdapter<Book, SearchBookAdapter.BookViewHolder>(BookDiff) {

    inner class BookViewHolder(private val binding: ItemBookRowBinding) : RecyclerView.ViewHolder(binding.root) {
        init {
            binding.root.setOnClickListener {
                if (bindingAdapterPosition != RecyclerView.NO_POSITION) {
                    onClickItem(getItem(bindingAdapterPosition))
                }
            }
        }

        fun bind(book: Book) {
            binding.tvTitle.text = book.title
            binding.tvAuthor.text = book.authors?.joinToString(", ") ?: ""
            binding.imgCover.loadCover(book.cover_image)
            binding.btnAction.visibility = View.GONE
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BookViewHolder {
        val binding = ItemBookRowBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return BookViewHolder(binding)
    }

    override fun onBindViewHolder(holder: BookViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

}
