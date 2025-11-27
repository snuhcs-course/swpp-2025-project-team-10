package com.example.librarytogether.feature.search.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SearchRepository @Inject constructor(
    private val api: SearchApi
) {
    suspend fun search(query: String): List<SearchItem> {
        return try {
            val res = api.search(query)
            if (res.isSuccessful) {
                res.body() ?: emptyList()
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("SearchRepository", "Error searching", e)
            throw e
        }
    }
}
