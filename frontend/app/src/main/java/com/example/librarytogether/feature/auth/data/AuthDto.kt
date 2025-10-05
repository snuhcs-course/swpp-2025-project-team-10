package com.example.librarytogether.feature.auth.data

//data class ApiResponse<T>(
//    val success: Boolean,
//    val data: T? = null,
//    val message: String? = null,
//    val error: ApiError? = null,
//    val pagination: Pagination? = null
//)
//
//data class ApiError(
//    val code: String,
//    val message: String,
//    val details: Map<String, Any>? = null
//)
//
//data class Pagination(
//    val page: Int,
//    val size: Int,
//    val total: Int,
//    val total_pages: Int
//)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val ok: Boolean,
    val accessToken: String,
    val refreshToken: String,
    val user: String? = null,
    val message: String? = null
)

data class RefreshRequest(
    val refreshToken: String
)

data class RefreshResponse(
    val accessToken: String,
    val refreshToken: String
)

data class SignUpRequest(
    val username: String,
    val password: String,
    val email: String
)

data class SignUpResponse(
    val ok: Boolean,
)

data class ForgotPasswordRequest(
    val email: String,
)

data class ForgotPasswordResponse(
    val requestId: String,
)

data class ForgotVerifyRequest(
    val requestId: String,
    val code: String
)

data class ForgotVerifyResponse(
    val ok: Boolean
)

data class ForgotResetRequest(
    val password: String,
)

data class ForgotResetResponse(
    val ok: Boolean,
)
data class GoogleAuthRequest(
    val idToken: String
)

data class GoogleAuthResponse(
    val ok: Boolean,
    val accessToken: String?,
    val refreshToken: String?,
    val message: String?
)

data class KakaoAuthRequest(
    val accessToken: String
)

data class KakaoAuthResponse(
    val ok: Boolean,
    val accessToken: String?,
    val refreshToken: String?,
    val message: String?
)

