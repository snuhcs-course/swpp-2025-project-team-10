package com.example.librarytogether.feature.barterapproval.data

import com.example.librarytogether.feature.library.data.Book

data class BarterApprovalDetail(
    val id: String,
    val requesterName: String,
    val requesterAvatarUrl: String?,
    val createdAt: String,
    val books: List<Book>,
    val message: List<String>,
)
