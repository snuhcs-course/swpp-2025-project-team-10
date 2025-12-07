package com.example.librarytogether.feature.comment

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.PopupMenu
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.feature.comment.data.CommentDto

class CommentAdapter(
    private val items: MutableList<CommentDto>,
    private var currentUserName: String,
    private val onLike: (CommentDto) -> Unit,
    private val onDelete: (CommentDto) -> Unit,
    private val onEdit: (CommentDto) -> Unit,
) : RecyclerView.Adapter<CommentAdapter.VH>() {

    inner class VH(v: View) : RecyclerView.ViewHolder(v) {
        private val tvAuthor = v.findViewById<TextView>(R.id.tvAuthor)
        private val tvComment = v.findViewById<TextView>(R.id.tvComment)
        private val tvCreatedAt = v.findViewById<TextView>(R.id.tvCreatedAt)
        private val ivProfile = v.findViewById<ImageView>(R.id.imgProfile)
        private val btnMore = v.findViewById<ImageView>(R.id.btnMore)

        private val btnLike = v.findViewById<ImageView>(R.id.btnLike)
        private val tvLikeCount = v.findViewById<TextView>(R.id.tvLikeCount)

        fun bind(dto: CommentDto) {
            tvAuthor.text = dto.authorName
            tvComment.text = dto.content

            // 날짜 포맷팅
            tvCreatedAt.text = dto.createdAt.take(10)

            val profileUrl = dto.authorProfile?.profilePicture
            Glide.with(itemView.context)
                .load(profileUrl)
                .placeholder(R.drawable.person_icon)
                .error(R.drawable.person_icon)
                .circleCrop()
                .into(ivProfile)

            // 좋아요 UI 설정
            tvLikeCount.text = dto.likeCount.toString()
            btnLike.setImageResource(
                if (dto.isLiked) R.drawable.ic_heart_filled
                else R.drawable.ic_heart_outline
            )
            btnLike.setOnClickListener { onLike(dto) }

            // [본인 확인 로직] 이름이 같을 때만 더보기 버튼 표시
            if (dto.authorName == currentUserName) {
                btnMore.visibility = View.VISIBLE
                btnMore.setOnClickListener { showMenu(dto, btnMore) }
            } else {
                btnMore.visibility = View.GONE
            }
        }

        private fun showMenu(dto: CommentDto, anchor: View) {
            val menu = PopupMenu(anchor.context, anchor)
            menu.inflate(R.menu.menu_comment)
            menu.setOnMenuItemClickListener {
                when (it.itemId) {
                    R.id.action_edit -> onEdit(dto)
                    R.id.action_delete -> onDelete(dto)
                }
                true
            }
            menu.show()
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_comment, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size

    fun updateComments(newItems: List<CommentDto>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    // 내 이름이 업데이트되었을 때 호출
    fun updateMyName(name: String) {
        Log.d("CommentAdapter", "이름 업데이트: $name")
        this.currentUserName = name
        notifyDataSetChanged()
    }
}
