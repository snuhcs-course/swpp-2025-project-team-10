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

data class UserInfo(
    val id: Int,
    val username: String,
    val email: String,
    val first_name: String? = null,
    val last_name: String? = null,
    val bio: String? = null,
    val location: String? = null,
    val birth_date: String? = null,
    val profile_picture: String? = null,
    val phone_number: String? = null,
    val is_profile_public: Boolean? = null,
    val allow_direct_messages: Boolean? = null,
    val reputation_score: Int? = null,
    val successful_trades: Int? = null,
    val follower_count: Int? = null,
    val following_count: Int? = null,
    val books_count: Int? = null,
    val created_at: String? = null,
    val last_active: String? = null
)

data class LoginResponse(
    val ok: Boolean,
    val accessToken: String,
    val refreshToken: String,
    val user: UserInfo? = null,
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
    val message: String? = null,
    val user: UserInfo? = null,
    val errors: Map<String, List<String>>? = null
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

