package com.example.librarytogether.feature.library

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.R
import com.example.librarytogether.feature.home.FeedClicks
import com.example.librarytogether.feature.library.data.Review

data class ReviewClicks(
    val onClickLike: (Review) -> Unit = {},
    val onClickReview: (Review) -> Unit = {},
    val onClickExchange: (Review) -> Unit = {},
    val onClickMore: (Review) -> Unit = {},
    val onClickProfile: (Review) -> Unit = {},
    val onClickUserName: (Review) -> Unit = {},
    val onClickTitle: (Review) -> Unit = {},
    val onClickAuthor: (Review) -> Unit = {},
    val onClickContent: (Review) -> Unit = {},
)
class ReviewAdapter(
    private val clicks: ReviewClicks = ReviewClicks()
) : ListAdapter<Review, ReviewAdapter.ReviewVH>(ReviewDiff) {

    inner class ReviewVH(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvBookTitle: TextView = itemView.findViewById(R.id.tvTitle)
        private val tvCreatedAt: TextView = itemView.findViewById(R.id.tvTime)

        fun bind(item: Review) {
            tvBookTitle.text = item.bookTitle
            tvCreatedAt.text = item.createdAt
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ReviewVH {
        val v = LayoutInflater.from(parent.context)
            .inflate(R.layout.feed_post, parent, false)
        return ReviewVH(v)
    }

    override fun onBindViewHolder(holder: ReviewVH, position: Int) {
        holder.bind(getItem(position))
    }
}