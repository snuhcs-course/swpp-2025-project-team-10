package com.example.librarytogether.feature.home

import android.content.res.ColorStateList
import android.text.TextUtils
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.constraintlayout.widget.ConstraintSet
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import androidx.viewpager2.widget.ViewPager2
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FeedPostBinding
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.util.TimeUtils
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
            current = post

            tvAuthor.text = post.authorName
            tvPoster.text = post.posterName
            tvContent.text = post.content
            tvTitle.text = post.bookTitle
            Glide.with(ivProfileImage.context)
                .load(post.posterProfile)
                .placeholder(R.drawable.person_icon)
                .circleCrop()
                .into(ivProfileImage)
            tvTime.text = TimeUtils.relativeTime(itemView.context, post.createdAt)

            pageCallback?.let { vpImages.unregisterOnPageChangeCallback(it) }
            pageCallback = null
            dotsMediator?.detach()
            dotsMediator = null

            val images = post.imageUrls
            mcPostImage.isVisible = images.isNotEmpty()
            val cs = ConstraintSet().apply { clone(contentFeed) }

            if (images.isNotEmpty()) {
                vpImages.adapter = ImagePagerAdapter(images)
                vpImages.offscreenPageLimit = 1
                dotsMediator?.detach()
                dotsMediator = TabLayoutMediator(tabDots, vpImages) { tab, _ ->
                    tab.setCustomView(R.layout.item_dot_tab)
                }.also {it.attach()}

                vpImages.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
                    override fun onPageSelected(position: Int) {
                        super.onPageSelected(position)
                        for (i in 0 until tabDots.tabCount) {
                            val dot = tabDots.getTabAt(i)?.customView
                            val bg = if (i == position)
                                R.drawable.dot_selected else R.drawable.dot_unselected
                            dot?.setBackgroundResource(bg)
                        }
                    }
                })
                cs.clear(binding.actionBar.id, ConstraintSet.TOP)
                cs.connect(binding.actionBar.id, ConstraintSet.TOP, binding.mcPostImage.id, ConstraintSet.BOTTOM)
                cs.clear(binding.tvContent.id, ConstraintSet.TOP)
                cs.connect(binding.tvContent.id, ConstraintSet.TOP, binding.actionBar.id, ConstraintSet.BOTTOM)
                cs.clear(binding.tvTime.id, ConstraintSet.TOP)
                cs.connect(binding.tvTime.id, ConstraintSet.TOP, binding.tvContent.id, ConstraintSet.BOTTOM)
                cs.applyTo(contentFeed)
            } else {
                dotsMediator?.detach()
                dotsMediator = null
                cs.clear(binding.actionBar.id, ConstraintSet.TOP)
                cs.connect(binding.actionBar.id, ConstraintSet.TOP, binding.tvContent.id, ConstraintSet.BOTTOM)
                cs.clear(binding.tvContent.id, ConstraintSet.TOP)
                cs.connect(binding.tvContent.id, ConstraintSet.TOP, binding.mcPostImage.id, ConstraintSet.BOTTOM)
                cs.clear(binding.tvTime.id, ConstraintSet.TOP)
                cs.connect(binding.tvTime.id, ConstraintSet.TOP, binding.actionBar.id, ConstraintSet.BOTTOM)
                cs.applyTo(contentFeed)
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

            val likeIconColor = if (post.isLiked) {
                ContextCompat.getColor(itemView.context, R.color.red)
            } else {
                ContextCompat.getColor(itemView.context, R.color.black)
            }
            binding.btnLike.iconTint = ColorStateList.valueOf(likeIconColor)
        }
    }
}
