package com.example.librarytogether.feature.search.data

data class SearchItem(
    val id: Int,
    val bookTitle: String,
    val authorName: String,
    val coverUrl: String? = null,
    val userBookId: Int? = null
)

data class SearchResponse(
    val results: List<SearchItem>
)
