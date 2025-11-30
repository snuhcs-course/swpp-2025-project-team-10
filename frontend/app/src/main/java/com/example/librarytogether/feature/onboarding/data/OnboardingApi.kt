package com.example.librarytogether.feature.onboarding.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface OnboardingApi {

    @POST("auth/onboarding/submit/")
    suspend fun submit(@Body body: OnboardingSubmitRequest): Response<Unit>
}
