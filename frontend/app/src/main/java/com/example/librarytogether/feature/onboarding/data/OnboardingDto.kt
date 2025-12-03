package com.example.librarytogether.feature.onboarding.data

data class LabelId(
    val id: Int,
    val name: String
)

data class OnboardingSubmitRequest(
    val book_ids: List<Int>,
    val author_ids: List<Int>,
    val genre_ids: List<Int>
)
