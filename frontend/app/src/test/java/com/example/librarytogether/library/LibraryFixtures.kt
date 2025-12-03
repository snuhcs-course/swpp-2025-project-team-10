package com.example.librarytogether.feature.library

import com.example.librarytogether.feature.library.data.*

object LibraryFixtures {

    fun review(id: Int, liked: Boolean = false, likeCount: Int = 0) = Review(
        id = id,
        bookTitle = "T$id",
        authorName = "A$id",
        userName = "U$id",
        userProfile = "",
        content = "C$id",
        imageUrls = emptyList(),
        likeCount = likeCount,
        createdAt = "2025-10-%02dT00:00:00Z".format(30 - id),
        isLiked = liked
    )

    fun book(id: Int) = Book(
        id = id.toString(),
        title = "B$id",
        authors = listOf("Auth$id"),
        cover_image = null,
        publisher = "Pub$id",
        isbn = "ISBN$id",
        publicationId = null
    )

    fun postBook() = PostBook(
        title = "B",
        authors = "Auth",
        cover_image = null,
        publisher = "Pub",
        isbn = "ISBN",
        is_for_barter = false,
        publication = "1234",
    )

    fun userPrefs() = UserPreferences(
        tradeLocation1 = "L1", tradeLocation2 = "L2",
        tradeSpot1 = "S1", tradeSpot2 = "S2",
        favBooks = listOf("FB"), favBookNotes = listOf("FBN"),
        favAuthors = listOf("FA"), favAuthorNotes = listOf("FAN"),
        readingHabit = "Night"
    )

    fun profile(bio: String? = "hi") = UserProfile(
        username = "me",
        bio = bio,
        profileUrl = null,
        reviewCount = 2,
        followerCount = 3,
        followingCount = 4,
        favoriteGenres = listOf("SF", "History"),
        preferences = userPrefs()
    )

    fun postReview() = PostReview(
        bookTitle = "New",
        authorName = "AA",
        content = "Body",
        publisher = "PUB",
        isbn = "ISBN",
        imageUrls = emptyList()
    )
}
