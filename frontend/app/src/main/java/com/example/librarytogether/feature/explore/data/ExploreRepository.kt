package com.example.librarytogether.feature.explore.data

import com.example.librarytogether.feature.library.data.Book
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ExploreRepository @Inject constructor(
    private val api: ExploreApi
) {
    suspend fun getRecommendations(): List<Book> {
        val res = api.getRecommendations()
        if (res.isSuccessful) {
            return res.body().orEmpty()
        } else {
            throw IllegalStateException("Failed: ${res.code()}")
        }
    }
}
