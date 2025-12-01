package com.example.librarytogether.feature.notification

import android.graphics.Typeface
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.feature.notification.data.NotificationDto
import com.example.librarytogether.util.TimeUtils
import de.hdodenhof.circleimageview.CircleImageView

data class NotificationClicks(
    val onClickItem: (NotificationDto) -> Unit = {},
    val onClickAction: (NotificationDto) -> Unit = {}
)

class NotificationAdapter(
    private val clicks: NotificationClicks
) : ListAdapter<NotificationDto, NotificationAdapter.NotiVH>(Diff) {

    companion object Diff : DiffUtil.ItemCallback<NotificationDto>() {
        override fun areItemsTheSame(oldItem: NotificationDto, newItem: NotificationDto): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: NotificationDto, newItem: NotificationDto): Boolean =
            oldItem == newItem
    }

    inner class NotiVH(v: View) : RecyclerView.ViewHolder(v) {
        private val imgProfile = v.findViewById<CircleImageView>(R.id.imgProfile)
        private val tvUser = v.findViewById<TextView>(R.id.tvUser)
        private val tvBody = v.findViewById<TextView>(R.id.tvBody)
        private val tvTime = v.findViewById<TextView>(R.id.tvTime)
        private val btnAction = v.findViewById<Button>(R.id.btnAction)

        fun bind(item: NotificationDto) {
            tvUser.text = item.title
            tvBody.text = item.body
            tvTime.text = TimeUtils.relativeTime(itemView.context, item.created_at)
            tvUser.setTypeface(null, if (item.is_read) Typeface.NORMAL else Typeface.BOLD)

            Glide.with(itemView)
                .load(R.drawable.sample_profile)
                .into(imgProfile)

            when (item.type) {
                "barter_request" -> {
                    btnAction.visibility = View.VISIBLE
                    btnAction.text = "교환 보기"
                }
                "barter_request_sent" -> {
                    btnAction.visibility = View.VISIBLE
                    btnAction.text = "교환 취소"
                }
                else -> {
                    btnAction.visibility = View.GONE
                }
            }

            itemView.setOnClickListener { clicks.onClickItem(item) }
            btnAction.setOnClickListener { clicks.onClickAction(item) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotiVH {
        val v = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_notification, parent, false)
        return NotiVH(v)
    }

    override fun onBindViewHolder(holder: NotiVH, position: Int) {
        holder.bind(getItem(position))
    }
}
