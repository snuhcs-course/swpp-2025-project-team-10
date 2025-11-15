package com.example.librarytogether.feature.search.data

data class SearchItem(
    val id: String,
    val title: String,
    val authors: String,
    val publisher: String?,
    val isbn: String?,
    val coverImage: String? = null,
    val isForBarter: Boolean?
)

data class SearchResponse(
    val results: List<SearchItem>
)
