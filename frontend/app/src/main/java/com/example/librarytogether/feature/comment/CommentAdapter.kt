package com.example.librarytogether.feature.comment

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.R
import com.example.librarytogether.feature.comment.data.CommentDto

class CommentAdapter(
    private val items: MutableList<CommentDto>
) : RecyclerView.Adapter<CommentAdapter.CommentVH>() {

    inner class CommentVH(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvAuthor = itemView.findViewById<TextView>(R.id.tvAuthor)
        private val tvComment = itemView.findViewById<TextView>(R.id.tvComment)
        private val tvCreatedAt = itemView.findViewById<TextView>(R.id.tvCreatedAt)
        private val imgProfile = itemView.findViewById<ImageView>(R.id.imgProfile)

        fun bind(dto: CommentDto) {
            tvAuthor.text = dto.author
            tvComment.text = dto.content
            tvCreatedAt.text = formatTime(dto.createdAt)

            // 프로필 이미지가 실제 없다면 기본 placeholder 사용
            imgProfile.setImageResource(R.drawable.person_icon)
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

    private fun formatTime(time: Long): String {
        val diff = System.currentTimeMillis() - time
        val minutes = diff / 60000
        return when {
            minutes < 1 -> "방금 전"
            minutes < 60 -> "${minutes}분 전"
            minutes < 60 * 24 -> "${minutes / 60}시간 전"
            else -> "${minutes / 1440}일 전"
        }
    }
}
