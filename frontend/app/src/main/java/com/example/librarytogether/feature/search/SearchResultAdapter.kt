package com.example.librarytogether.feature.search

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.databinding.ItemBookRowBinding
import com.example.librarytogether.feature.search.data.SearchItem

class SearchResultAdapter(
    private val onClick: (SearchItem) -> Unit
) : ListAdapter<SearchItem, SearchResultAdapter.VH>(DIFF) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemBookRowBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return VH(binding, onClick)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }

    class VH(
        private val binding: ItemBookRowBinding,
        private val onClick: (SearchItem) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: SearchItem) {
            binding.tvTitle.text = item.title
            binding.tvAuthor.text = item.author
            Glide.with(binding.imgCover).load(item.cover_image).into(binding.imgCover)

            binding.root.setOnClickListener { onClick(item) }
        }
    }

    private object DIFF : DiffUtil.ItemCallback<SearchItem>() {
        override fun areItemsTheSame(o: SearchItem, n: SearchItem) = o.id == n.id
        override fun areContentsTheSame(o: SearchItem, n: SearchItem) = o == n
    }
}
