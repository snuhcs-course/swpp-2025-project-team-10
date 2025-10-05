package com.example.librarytogether.feature.auth.data

import com.example.librarytogether.feature.auth.ForgotPasswordActivity
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {
    @POST("auth/login/")
    suspend fun login(@Body body: LoginRequest): Response<LoginResponse>

    @POST("auth/token/refresh/")
    suspend fun refresh(@Body body: RefreshRequest): Response<RefreshResponse>

    @POST("auth/signup/")
    suspend fun signUp(@Body body: SignUpRequest): Response<SignUpResponse>

    @POST("auth/forgot/start/")
    suspend fun forgotPassword(@Body body: ForgotPasswordRequest): Response<ForgotPasswordResponse>

    @POST("auth/forgot/verify/")
    suspend fun forgotVerify(@Body body: ForgotVerifyRequest): Response<ForgotVerifyResponse>

    @POST("auth/forgot/reset/")
    suspend fun forgotReset(@Body body: ForgotResetRequest): Response<ForgotResetResponse>

    @POST("auth/signup/google/")
    suspend fun googleSignup(@Body body: GoogleAuthRequest): Response<GoogleAuthResponse>

    @POST("auth/login/google/")
    suspend fun googleLogin(@Body body: GoogleAuthRequest): Response<GoogleAuthResponse>

    @POST("auth/signup/kakao/")
    suspend fun kakaoSignup(@Body request: KakaoAuthRequest): Response<KakaoAuthResponse>

    @POST("auth/login/kakao/")
    suspend fun kakaoLogin(@Body request: KakaoAuthRequest): Response<KakaoAuthResponse>


}
