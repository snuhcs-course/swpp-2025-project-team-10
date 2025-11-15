package com.example.librarytogether.feature.library

import android.content.res.ColorStateList
import android.text.TextUtils
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import androidx.viewpager2.widget.ViewPager2
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FeedPostBinding // [수정] ViewBinding import
import com.example.librarytogether.feature.home.ImagePagerAdapter // [추가] FeedAdapter가 사용하던 ImagePagerAdapter
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.util.TimeUtils
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.tabs.TabLayoutMediator

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

    private val expandedIds = mutableSetOf<Int>()
    private companion object {
        const val MAX_LINES = 3
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ReviewVH {
        val binding = FeedPostBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ReviewVH(binding, clicks)
    }

    override fun onBindViewHolder(holder: ReviewVH, position: Int) {
        holder.bind(getItem(position))
    }

    fun toggleExpand(reviewId: Int) {
        val idx = currentList.indexOfFirst { it.id == reviewId }
        if (idx == -1) return
        if (expandedIds.contains(reviewId)) expandedIds.remove(reviewId) else expandedIds.add(reviewId)
        notifyItemChanged(idx)
    }

    inner class ReviewVH(
        private val binding: FeedPostBinding,
        private val clicks: ReviewClicks
    ) : RecyclerView.ViewHolder(binding.root) {

        private var dotsMediator: TabLayoutMediator? = null
        private var pageCallback: ViewPager2.OnPageChangeCallback? = null
        private var current: Review? = null

        init {
            with(binding) {
                fun View.safeClick(action: (Review) -> Unit) = setOnClickListener {
                    val p = bindingAdapterPosition
                    val review = current ?: return@setOnClickListener // 'current' 사용
                    if (p != RecyclerView.NO_POSITION) action(review)
                }

                btnLike.safeClick(clicks.onClickLike)
                btnBookReview.safeClick(clicks.onClickReview)
                btnExchange.safeClick(clicks.onClickExchange)
                btnAdd.safeClick(clicks.onClickMore) // btnAdd는 UI상 '더보기'가 아닐 수 있으나, FeedAdapter 구조를 따름
                btnMore.safeClick(clicks.onClickMore)
                ivProfileImage.safeClick(clicks.onClickProfile)
                tvPoster.safeClick(clicks.onClickUserName)
                tvTitle.safeClick(clicks.onClickTitle)
                tvAuthor.safeClick(clicks.onClickAuthor)
                tvContent.safeClick(clicks.onClickContent)
            }
        }

        fun bind(item: Review) = with(binding) {
            current = item

            tvPoster.text = item.userName
            tvTitle.text = item.bookTitle
            tvAuthor.text = item.authorName
            tvContent.text = item.content
            tvTime.text = TimeUtils.relativeTime(itemView.context, item.createdAt)
            ivProfileImage.loadAvatar(item.userProfile)

            pageCallback?.let { vpImages.unregisterOnPageChangeCallback(it) }
            pageCallback = null
            dotsMediator?.detach()
            dotsMediator = null

            val images = item.imageUrls
            mcPostImage.isVisible = images.isNotEmpty()

            if (images.isNotEmpty()) {
                vpImages.adapter = ImagePagerAdapter(images)
                vpImages.offscreenPageLimit = 1
                dotsMediator = TabLayoutMediator(tabDots, vpImages) { tab, _ ->
                    tab.setCustomView(R.layout.item_dot_tab)
                }.also {it.attach()}

                pageCallback = object : ViewPager2.OnPageChangeCallback() {
                    override fun onPageSelected(position: Int) {
                        super.onPageSelected(position)
                        for (i in 0 until tabDots.tabCount) {
                            val dot = tabDots.getTabAt(i)?.customView
                            val bg = if (i == position)
                                R.drawable.dot_selected else R.drawable.dot_unselected
                            dot?.setBackgroundResource(bg)
                        }
                    }
                }.also { vpImages.registerOnPageChangeCallback(it) }
            } else {
                vpImages.adapter = null
                tabDots.removeAllTabs()
            }

            val isExpanded = expandedIds.contains(item.id)
            if (isExpanded) {
                tvContent.maxLines = Integer.MAX_VALUE
                tvContent.ellipsize = null
            }
            else {
                tvContent.maxLines = MAX_LINES
                tvContent.ellipsize = TextUtils.TruncateAt.END
            }

            val iconColor = if (item.isLiked) {
                ContextCompat.getColor(itemView.context, R.color.red)
            } else {
                ContextCompat.getColor(itemView.context, R.color.black)
            }

            if (item.isLiked) {
                btnLike.setIconResource(R.drawable.filled_like_icon)
            } else {
                btnLike.setIconResource(R.drawable.like_icon)
            }
            btnLike.iconTint = ColorStateList.valueOf(iconColor)
        }

        fun cleanup() = with(binding) {
            pageCallback?.let { vpImages.unregisterOnPageChangeCallback(it) }
            pageCallback = null
            dotsMediator?.detach()
            dotsMediator = null
            vpImages.adapter = null
            tabDots.removeAllTabs()
        }
    }

    override fun onViewRecycled(holder: ReviewVH) {
        holder.cleanup()
        super.onViewRecycled(holder)
    }
}

object ReviewDiff : DiffUtil.ItemCallback<Review>() {
    override fun areItemsTheSame(oldItem: Review, newItem: Review): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Review, newItem: Review): Boolean =
        oldItem == newItem
}
