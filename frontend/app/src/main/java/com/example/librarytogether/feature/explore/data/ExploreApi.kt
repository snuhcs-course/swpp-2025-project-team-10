package com.example.librarytogether.feature.explore.data

import com.example.librarytogether.feature.library.data.Book
import retrofit2.Response
import retrofit2.http.GET

interface ExploreApi {
    @GET("explore/recommendations/")
    suspend fun getRecommendations(): Response<List<Book>>
}

