package com.example.librarytogether.feature.comment

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
    private val currentUserName: String,
    private val onDelete: (CommentDto) -> Unit,
    private val onEdit: (CommentDto) -> Unit
) : RecyclerView.Adapter<CommentAdapter.CommentVH>() {

    inner class CommentVH(itemView: View) : RecyclerView.ViewHolder(itemView) {

        private val tvAuthor = itemView.findViewById<TextView>(R.id.tvAuthor)
        private val tvComment = itemView.findViewById<TextView>(R.id.tvComment)
        private val tvCreatedAt = itemView.findViewById<TextView>(R.id.tvCreatedAt)
        private val imgProfile = itemView.findViewById<ImageView>(R.id.imgProfile)
        private val btnMore = itemView.findViewById<ImageView>(R.id.btnMore)

        fun bind(dto: CommentDto) {
            tvAuthor.text = dto.authorName
            tvComment.text = dto.content
            tvCreatedAt.text = formatCreatedAt(dto.createdAt)

            // 🔥 프로필 이미지 로딩
            val profileUrl = dto.authorProfile?.profile_picture
            Glide.with(itemView.context)
                .load(profileUrl)
                .placeholder(R.drawable.person_icon)
                .error(R.drawable.person_icon)
                .circleCrop()
                .into(imgProfile)

            // 🔥 본인 댓글만 더보기 메뉴 표시
            if (dto.authorName == currentUserName) {
                btnMore.visibility = View.VISIBLE
                btnMore.setOnClickListener { showPopup(dto, btnMore) }
            } else {
                btnMore.visibility = View.GONE
            }
        }

        private fun showPopup(dto: CommentDto, anchor: View) {
            val menu = PopupMenu(anchor.context, anchor)
            menu.inflate(R.menu.menu_comment)  // 삭제/수정 메뉴 리소스 필요

            menu.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    R.id.action_edit -> {
                        onEdit(dto)
                        true
                    }
                    R.id.action_delete -> {
                        onDelete(dto)
                        true
                    }
                    else -> false
                }
            }

            menu.show()
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CommentVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_comment, parent, false)
        return CommentVH(view)
    }

    override fun onBindViewHolder(holder: CommentVH, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    fun updateComments(list: List<CommentDto>) {
        items.clear()
        items.addAll(list)
        notifyDataSetChanged()
    }

    // TODO: 이후 util 파일로 분리해도 좋음
    private fun formatCreatedAt(isoTime: String): String {
        return isoTime  // 실제로는 변환 필요하지만 지금은 원본 유지
    }
}
