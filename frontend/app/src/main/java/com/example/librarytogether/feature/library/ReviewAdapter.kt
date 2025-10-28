package com.example.librarytogether.feature.library

import android.content.res.ColorStateList
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.R
import com.example.librarytogether.feature.home.FeedClicks
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.button.MaterialButton

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
        private val tvUserName: TextView = itemView.findViewById(R.id.tvPoster)
        private val tvBookTitle: TextView = itemView.findViewById(R.id.tvTitle)
        private val tvAuthorName: TextView = itemView.findViewById(R.id.tvAuthor)
        private val tvContent: TextView = itemView.findViewById(R.id.tvContent)
        private val tvCreatedAt: TextView = itemView.findViewById(R.id.tvTime)

        private val btnLike: MaterialButton = itemView.findViewById(R.id.btnLike)

        private val img: ImageView = itemView.findViewById(R.id.ivProfileImage)

        fun bind(item: Review) {
            tvUserName.text = item.userName
            tvBookTitle.text = item.bookTitle
            tvAuthorName.text = item.authorName
            tvContent.text = item.content
            tvCreatedAt.text = item.createdAt
            btnLike.setOnClickListener {
                clicks.onClickLike(item)
            }
            img.loadAvatar(item.userProfile)

            val likeIconColor = if (item.isLiked) {
                ContextCompat.getColor(itemView.context, R.color.red)
            } else {
                ContextCompat.getColor(itemView.context, R.color.black)
            }
            btnLike.iconTint = ColorStateList.valueOf(likeIconColor)
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
