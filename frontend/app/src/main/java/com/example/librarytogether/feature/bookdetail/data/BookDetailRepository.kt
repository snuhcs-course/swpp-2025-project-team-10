package com.example.librarytogether.feature.bookdetail.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BookRepository @Inject constructor(
    private val bookApi: BookDetailApi
) {
    suspend fun getBookDetail(id: String): BookDetail {
        return try {
            val response = bookApi.getBook(id)
            if (response.isSuccessful) {
                response.body()
                    ?: throw IllegalStateException("Empty body for bookId=$id")
            } else {
                throw IllegalStateException("Failed to get book detail: ${response.code()}")
            }
        } catch (e: Exception) {
            Log.e("BookRepository", "Error fetching book detail (id=$id)", e)
            throw e
        }
    }
}
