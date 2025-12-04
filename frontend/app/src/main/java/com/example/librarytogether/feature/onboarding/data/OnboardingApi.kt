package com.example.librarytogether.feature.onboarding.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface OnboardingApi {

    @GET("library/onboarding/books/")
    suspend fun getBooks(): List<OnboardingItem>

    @GET("library/onboarding/authors/")
    suspend fun getAuthors(): List<OnboardingItem>

    @GET("library/onboarding/genres/")
    suspend fun getGenres(): List<OnboardingItem>

    @POST("auth/users/onboarding/") // 온보딩 결과 제출 경로는 auth/users/onboarding/ 으로 변경.
    suspend fun submit(@Body request: OnboardingSubmitRequest): Response<Unit>
}
