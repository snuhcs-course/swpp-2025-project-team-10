package com.example.librarytogether.feature.bookdetail.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

interface BookDetailApi {
    @GET("books/{id}/")
    suspend fun getBook(@Path("id") id: String): Response<BookDetail>
}
