package com.example.librarytogether.feature.home

import android.content.res.ColorStateList
import android.provider.CalendarContract
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
import com.example.librarytogether.databinding.FeedPostBinding
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.util.TimeUtils
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.tabs.TabLayoutMediator

data class FeedClicks(
    val onClickLike: (Post) -> Unit = {},
    val onClickReview: (Post) -> Unit = {},
    val onClickExchange: (Post) -> Unit = {},
    val onClickAdd: (Post) -> Unit = {},
    val onClickMore: (Post) -> Unit = {},
    val onClickProfile: (Post) -> Unit = {},
    val onClickUserName: (Post) -> Unit = {},
    val onClickTitle: (Post) -> Unit = {},
    val onClickAuthor: (Post) -> Unit = {},
    val onClickContent: (Post) -> Unit = {},
)
class FeedAdapter(
    private val clicks: FeedClicks = FeedClicks()
) : ListAdapter<Post, FeedAdapter.PostVH>(PostDiff) {

    private val expandedIds = mutableSetOf<Int>()
    private companion object {
        const val MAX_LINES = 3
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PostVH {
        val binding = FeedPostBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return PostVH(binding, clicks)
    }

    override fun onBindViewHolder(holder: PostVH, position: Int) {
        holder.bind(getItem(position))
    }

    fun toggleExpand(postId: Int) {
        val idx = currentList.indexOfFirst { it.id == postId }
        if (idx == -1) return
        if (expandedIds.contains(postId)) expandedIds.remove(postId) else expandedIds.add(postId)
        notifyItemChanged(idx)
    }

    inner class PostVH(
        private val binding: FeedPostBinding,
        private val clicks: FeedClicks
    ) : RecyclerView.ViewHolder(binding.root) {
        private var dotsMediator: TabLayoutMediator? = null
        private var pageCallback: ViewPager2.OnPageChangeCallback? = null

        private var current: Post? = null

        private val defaultLikeIconTint = binding.btnLike.iconTint
        private val enabledExchangeTextColors = binding.btnExchange.textColors
        private val enabledExchangeIconTint = binding.btnExchange.iconTint

        init {
            with(binding) {
                fun View.safeClick(action: (Post) -> Unit) = setOnClickListener {
                    val p = bindingAdapterPosition
                    val post = current ?: return@setOnClickListener
                    if (p != RecyclerView.NO_POSITION) action(post)
                }

                btnLike.safeClick(clicks.onClickLike)
                btnBookReview.safeClick(clicks.onClickReview)
                btnExchange.safeClick(clicks.onClickExchange)
                btnAdd.safeClick(clicks.onClickAdd)
                btnMore.safeClick(clicks.onClickMore)
                ivProfileImage.safeClick(clicks.onClickProfile)
                tvPoster.safeClick(clicks.onClickUserName)
                tvTitle.safeClick(clicks.onClickTitle)
                tvAuthor.safeClick(clicks.onClickAuthor)
                tvContent.safeClick(clicks.onClickContent)
            }
        }

        fun bind(post: Post) = with(binding) {

            // UI Initialize (재활용 잔상 제거)
            tvAuthor.text = ""
            tvPoster.text = ""
            tvTitle.text = ""
            tvContent.text = ""
            ivProfileImage.setImageDrawable(null)
            vpImages.adapter = null
            tabDots.removeAllTabs()
            mcPostImage.isVisible = false
            tvContent.maxLines = MAX_LINES
            tvContent.ellipsize = TextUtils.TruncateAt.END

            current = post

            tvAuthor.text = post.authorName
            tvPoster.text = post.posterName
            tvContent.text = post.content
            tvTitle.text = post.bookTitle
            ivProfileImage.loadAvatar(post.posterProfile)
            tvTime.text = TimeUtils.relativeTime(itemView.context, post.createdAt)

            pageCallback?.let { vpImages.unregisterOnPageChangeCallback(it) }
            pageCallback = null
            dotsMediator?.detach()
            dotsMediator = null

            val images = post.imageUrls
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

//                tabDots.post {
//                    for (i in 0 until tabDots.tabCount) {
//                        val dot = tabDots.getTabAt(i)?.customView
//                        val bg = if (i == 0) R.drawable.dot_selected else R.drawable.dot_unselected
//                        dot?.setBackgroundResource(bg)
//                    }
//                }
            } else {
                vpImages.adapter = null
                tabDots.removeAllTabs()
            }

            val isExpanded = expandedIds.contains(post.id)
            if (isExpanded) {
                tvContent.maxLines = Integer.MAX_VALUE
                tvContent.ellipsize = null
            }
            else {
                tvContent.maxLines = MAX_LINES
                tvContent.ellipsize = TextUtils.TruncateAt.END
            }

            val IconColor = if (post.isLiked) {
                val red = ContextCompat.getColor(itemView.context, R.color.red)
                ColorStateList.valueOf(red)
            } else {
                defaultLikeIconTint
            }
            btnLike.iconTint = IconColor

            if (post.isLiked) {
                btnLike.setIconResource(R.drawable.filled_like_icon)
            } else {
                btnLike.setIconResource(R.drawable.like_icon)
            }

            val barterAvailable = post.bookAvailableForBarter

            btnExchange.isEnabled = barterAvailable

            if (barterAvailable) {
                btnExchange.isEnabled = true
                btnExchange.setTextColor(enabledExchangeTextColors)
                btnExchange.iconTint = enabledExchangeIconTint
            } else {
                btnExchange.isEnabled = false
                val disabledColor = ContextCompat.getColor(itemView.context, R.color.light_gray)
                btnExchange.setTextColor(disabledColor)
                btnExchange.iconTint = ColorStateList.valueOf(disabledColor)
            }
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

    override fun onViewRecycled(holder: PostVH) {
        holder.cleanup()
        super.onViewRecycled(holder)
    }
}

object PostDiff : DiffUtil.ItemCallback<Post>() {
    override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean =
        oldItem.id == newItem.id


    override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean {
        return oldItem == newItem
    }

}
