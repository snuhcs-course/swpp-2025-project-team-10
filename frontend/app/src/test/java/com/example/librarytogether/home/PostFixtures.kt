package com.example.librarytogether.feature.home

import com.example.librarytogether.feature.home.data.Post

object PostFixtures {
    fun post(
        id: Int = 1,
        likeCount: Int = 0,
        liked: Boolean = false,
        createdAt: String? = null
    ): Post = Post(
        id = id,
        posterId = 100 + id,
        bookTitle = "Book$id",
        authorName = "Author$id",
        posterName = "User$id",
        posterProfile = "profile$id.png",
        content = "Content$id",
        imageUrls = emptyList(),
        likeCount = likeCount,
        createdAt = createdAt,
        isLiked = liked,
        bookId = "book-$id",
        bookAvailableForBarter = true
    )
}
