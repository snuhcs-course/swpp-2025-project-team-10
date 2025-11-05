package com.example.librarytogether.feature.home

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.util.loadFeed
import com.google.android.material.imageview.ShapeableImageView

class ImagePagerAdapter(
    private val urls: List<String>
) : RecyclerView.Adapter<ImagePagerAdapter.ImageVH>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ImageVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.feed_post_image_page, parent, false)
        return ImageVH(view)
    }

    override fun onBindViewHolder(holder: ImageVH, position: Int) {
        holder.bind(urls[position])
    }

    override fun getItemCount(): Int = urls.size

    class ImageVH(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val iv = itemView.findViewById<ShapeableImageView>(R.id.ivPage)

        fun bind(url: String) {
            iv.loadFeed(url)
        }
    }
}
