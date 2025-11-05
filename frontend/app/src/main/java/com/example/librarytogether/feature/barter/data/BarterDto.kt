package com.example.librarytogether.feature.barter.data

import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserProfile

data class BarterDetailResponse(
    val book: Book,
    val owner: UserProfile,
    val relatedReview: Review?
)

data class BarterOfferRequest(
    val userBookId: Int,
    val myBookId: Int,
    val message: String
)
