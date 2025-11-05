package com.example.librarytogether.feature.barter.data

import com.example.librarytogether.feature.library.data.Book
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface BarterApi {
    @GET("barter/{userBookId}/")
    suspend fun getBarterDetails(@Path("userBookId") userBookId: Int): Response<BarterDetailResponse>

    @POST("barter/offer/")
    suspend fun submitOffer(@Body offer: BarterOfferRequest): Response<Unit>

    @GET("library/books/")
    suspend fun getMyBooks(): Response<List<Book>>

    @GET("library/books/{id}/")
    suspend fun getBookById(@Path("id") bookId: Int): Response<Book>
}
