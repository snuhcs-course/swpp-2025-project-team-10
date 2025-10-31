package com.example.librarytogether.feature.notification

import android.graphics.Typeface
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.feature.notification.data.NotificationDto
import de.hdodenhof.circleimageview.CircleImageView

data class NotificationClicks(
    val onClickItem: (NotificationDto) -> Unit = {},
    val onClickAction: (NotificationDto) -> Unit = {}
)

class NotificationAdapter(
    private val clicks: NotificationClicks
) : ListAdapter<NotificationDto, NotificationAdapter.NotiVH>(NotificationDiff()) {

    inner class NotiVH(v: View) : RecyclerView.ViewHolder(v) {
        private val imgProfile = v.findViewById<CircleImageView>(R.id.imgProfile)
        private val tvUser = v.findViewById<TextView>(R.id.tvUser)
        private val tvBody = v.findViewById<TextView>(R.id.tvBody)
        private val tvTime = v.findViewById<TextView>(R.id.tvTime)
        private val btnAction = v.findViewById<Button>(R.id.btnAction)

        fun bind(item: NotificationDto) {
            tvUser.text = item.title
            tvBody.text = item.body
            tvTime.text = formatRelativeTime(item.createdAt)
            btnAction.text = "교환"
            tvUser.setTypeface(null, if (item.isRead) Typeface.NORMAL else Typeface.BOLD)
            Glide.with(itemView).load(R.drawable.sample_profile).into(imgProfile)

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

private fun formatRelativeTime(iso: String): String {
    return try {
        val time = java.time.OffsetDateTime.parse(iso)
        val diffMin = java.time.Duration.between(time, java.time.OffsetDateTime.now()).toMinutes()
        when {
            diffMin < 1 -> "방금 전"
            diffMin < 60 -> "${diffMin}분 전"
            diffMin < 60 * 24 -> "${diffMin / 60}시간 전"
            else -> "${diffMin / (60 * 24)}일 전"
        }
    } catch (e: Exception) {
        ""
    }
}

