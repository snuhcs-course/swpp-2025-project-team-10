package com.example.librarytogether.feature.library

import android.net.Uri
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.R

class PhotoAdapter(
    private val onRemove: (Uri) -> Unit
) : ListAdapter<Uri, PhotoAdapter.VH>(Diff) {

    object Diff : DiffUtil.ItemCallback<Uri>() {
        override fun areItemsTheSame(oldItem: Uri, newItem: Uri) = oldItem == newItem
        override fun areContentsTheSame(oldItem: Uri, newItem: Uri) = oldItem == newItem
    }

    inner class VH(parent: ViewGroup) :
        RecyclerView.ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_photo, parent, false)
        ) {
        private val iv: ImageView = itemView.findViewById(R.id.ivPhoto)

        fun bind(uri: Uri) {
            Glide.with(iv).load(uri).centerCrop().into(iv)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = VH(parent)
    override fun onBindViewHolder(holder: VH, position: Int) = holder.bind(getItem(position))
}
