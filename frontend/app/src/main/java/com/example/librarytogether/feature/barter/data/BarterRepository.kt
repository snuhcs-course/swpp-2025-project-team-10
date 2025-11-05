package com.example.librarytogether.feature.barter.data

import android.util.Log
import com.example.librarytogether.feature.library.data.Book
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BarterRepository @Inject constructor(
    private val barterApi: BarterApi
) {
    suspend fun getBarterDetails(userBookId: Int): BarterDetailResponse? {
        return try {
            val response = barterApi.getBarterDetails(userBookId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("BarterRepository", "getBarterDetails failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("BarterRepository", "Error fetching barter details", e)
            null
        }
    }

    suspend fun submitOffer(offer: BarterOfferRequest): Boolean {
        return try {
            val response = barterApi.submitOffer(offer)
            if (!response.isSuccessful) {
                Log.e("BarterRepository", "submitOffer failed: ${response.code()}")
            }
            response.isSuccessful
        } catch (e: Exception) {
            Log.e("BarterRepository", "Error submitting offer", e)
            false
        }
    }

    suspend fun getMyBooks(): List<Book>? {
        return try {
            val response = barterApi.getMyBooks()
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("BarterRepository", "getMyBooks failed: ${response.code()}")
                emptyList()
            }
        } catch (e: Exception) {
            Log.e("BarterRepository", "Error fetching my books", e)
            emptyList()
        }
    }

    suspend fun getBookById(bookId: Int): Book? {
        return try {
            val response = barterApi.getBookById(bookId)
            if (response.isSuccessful) {
                response.body()
            } else {
                Log.e("BarterRepository", "getBookById failed: ${response.code()}")
                null
            }
        } catch (e: Exception) {
            Log.e("BarterRepository", "Error fetching book by id", e)
            null
        }
    }
}
