package com.example.librarytogether.feature.search.data

data class SearchItem(
    val id: String,
    val title: String,
    val author: String,
    val publisher_name: String,
    val isbn: String?,
    val description: String,
    val cover_image: String? = null,
    val is_for_barter: Boolean?,
    val owner_notes: String? = null,
    val owner: String? = null
)

data class SearchResponse(
    val results: List<SearchItem>
)
