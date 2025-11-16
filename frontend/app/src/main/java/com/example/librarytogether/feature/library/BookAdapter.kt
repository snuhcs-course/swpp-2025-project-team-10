package com.example.librarytogether.feature.library

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.util.loadCover


enum class BookListMode { TILE, ROW }


data class BookClicks(
    val onClickItem: (Book) -> Unit,
    val onClickMore: (Book, View) -> Unit = { _, _ -> },
    val onSelect: (Book) -> Unit = {},
)

class BookAdapter(
    private var mode: BookListMode,
    private val clicks: BookClicks
) : ListAdapter<Book, RecyclerView.ViewHolder>(BookDiff) {

    fun setMode(newMode: BookListMode) {
        if (mode != newMode) {
            mode = newMode
            if (itemCount > 0) notifyItemRangeChanged(0, itemCount, "payload_mode_changed")
        }
    }

    override fun getItemViewType(position: Int): Int =
        if (mode == BookListMode.TILE) R.layout.item_book_tile
        else if (mode == BookListMode.ROW) R.layout.item_book_row
        else throw IllegalArgumentException("Unknown mode: $mode")

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val v: View = LayoutInflater.from(parent.context).inflate(viewType, parent, false)
        return if (viewType == R.layout.item_book_tile) TileVH(v, clicks) else RowVH(v, clicks)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item: Book = getItem(position)
        when (holder) {
            is TileVH -> holder.bind(item)
            is RowVH  -> holder.bind(item)
        }
    }

    // --- ViewHolders ---

    private class TileVH(
        itemView: View,
        private val clicks: BookClicks
    ) : RecyclerView.ViewHolder(itemView) {

        private val img: ImageView = itemView.findViewById(R.id.imgCover)

        fun bind(item: Book) {
            img.loadCover(item.cover_image)
            itemView.setOnClickListener { clicks.onClickItem(item) }
        }
    }

    private class RowVH(
        itemView: View,
        private val clicks: BookClicks
    ) : RecyclerView.ViewHolder(itemView) {

        private val img: ImageView   = itemView.findViewById(R.id.imgCover)
        private val tvTitle: TextView  = itemView.findViewById(R.id.tvTitle)
        private val tvAuthor: TextView = itemView.findViewById(R.id.tvAuthor)
        private val btnMore: View?     = itemView.findViewById(R.id.btnAction)  // 있으면 사용

        fun bind(item: Book) {
            img.loadCover(item.cover_image)
            tvTitle.text  = item.title
            tvAuthor.text = item.authors.orEmpty()

            itemView.setOnClickListener { clicks.onSelect(item) }
            btnMore?.setOnClickListener { v -> clicks.onClickMore(item, v) }
        }
    }
}

object BookDiff : DiffUtil.ItemCallback<Book>() {
    override fun areItemsTheSame(oldItem: Book, newItem: Book): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Book, newItem: Book): Boolean =
        oldItem == newItem
}
