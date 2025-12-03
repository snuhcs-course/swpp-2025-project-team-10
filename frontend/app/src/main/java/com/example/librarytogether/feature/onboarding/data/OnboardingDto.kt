package com.example.librarytogether.feature.onboarding.data

data class LabelId(
    val id: String, // Int에서 String으로 변경
    val label: String
)

data class OnboardingSubmitRequest(
    val book_ids: List<String>,
    val author_ids: List<Int>,
    val genre_ids: List<Int>
)

data class OnboardingItem(
    val id: String, // Int에서 String으로 변경
    val name: String
)
