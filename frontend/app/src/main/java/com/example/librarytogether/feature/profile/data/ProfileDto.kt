package com.example.librarytogether.feature.profile.data

import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences

data class UserProfile(
    val userId: Int,
    val username: String,
    val bio: String?,
    val profileUrl: String?,
    val reviewCount: Int = 0,
    val followerCount: Int = 0,
    val followingCount: Int = 0,
    val isFollowing: Boolean = false,
    val favoriteGenres: List<String>,
    val preferences: UserPreferences,
)

