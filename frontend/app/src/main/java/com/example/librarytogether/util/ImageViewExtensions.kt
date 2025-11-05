package com.example.librarytogether.util

import android.widget.ImageView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions
import com.example.librarytogether.R

fun ImageView.loadCover(
    url: String?,
    placeholderRes: Int = R.drawable.book_icon
) {
    Glide.with(this.context)
        .load(url)
        .placeholder(placeholderRes)
        .error(placeholderRes)
        .centerCrop()
        .transition(DrawableTransitionOptions.withCrossFade())
        .into(this)
}

fun ImageView.loadAvatar(
    url: String?,
    placeholderRes: Int = R.drawable.person_icon
) {
    Glide.with(this.context)
        .load(url)
        .placeholder(placeholderRes)
        .error(placeholderRes)
        .circleCrop()
        .transition(DrawableTransitionOptions.withCrossFade())
        .into(this)
}

fun ImageView.loadFeed(
    url: String?,
) {
    Glide.with(this.context)
        .load(url)
        .placeholder(android.R.color.darker_gray)
        .into(this)
}
