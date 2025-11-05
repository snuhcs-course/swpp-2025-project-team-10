package com.example.librarytogether.feature.search.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface SearchApi {
    @GET("search/")
    suspend fun search(@Query("q") query: String): Response<SearchResponse>
}
