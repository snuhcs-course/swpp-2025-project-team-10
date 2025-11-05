package com.example.librarytogether.home

import com.example.librarytogether.feature.home.data.Post

object PostFixtures {
    fun post(
        id: Int,
        title: String = "T$id",
        author: String = "A$id",
        poster: String = "U$id",
        liked: Boolean = false,
        likeCount: Int = 0,
        createdAt: String? = "2025-10-%02dT00:00:00Z".format(30 - id) // id가 작을수록 최신이 되게 예시
    ) = Post(
        id = id,
        bookTitle = title,
        authorName = author,
        posterName = poster,
        posterProfile = "",
        content = "C$id",
        imageUrls = emptyList(),
        likeCount = likeCount,
        createdAt = createdAt,
        userBookId = 1,
        isLiked = liked
    )
}
