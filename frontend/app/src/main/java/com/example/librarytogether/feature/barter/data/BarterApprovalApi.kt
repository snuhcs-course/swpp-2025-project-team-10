package com.example.librarytogether.feature.barterapproval.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface BarterApprovalApi {

    @GET("barter/requests/{id}/")
    suspend fun getBarterApproval(
        @Path("id") id: String
    ): Response<BarterApprovalDetail>

    @POST("barter/requests/{id}/accept/{bookId}/")
    suspend fun acceptBook(
        @Path("id") requestId: String,
        @Path("bookId") bookId: String
    ): Response<Unit>

    @POST("barter/requests/{id}/reject/")
    suspend fun rejectRequest(
        @Path("id") requestId: String
    ): Response<Unit>
}
