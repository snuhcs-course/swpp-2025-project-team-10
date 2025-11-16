package com.example.librarytogether.feature.comment

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.R

class CommentAdapter(
    private val items: MutableList<String>
) : RecyclerView.Adapter<CommentAdapter.CommentVH>() {

    inner class CommentVH(val view: TextView) : RecyclerView.ViewHolder(view) {
        fun bind(text: String) {
            view.text = text
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CommentVH {
        val v = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_comment, parent, false) as TextView
        return CommentVH(v)
    }

    override fun onBindViewHolder(holder: CommentVH, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    fun updateComments(list: List<String>) {
        items.clear()
        items.addAll(list)
        notifyDataSetChanged()
    }
}
