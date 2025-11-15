package com.example.librarytogether.network

import android.content.Context
import okhttp3.Authenticator
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.Route
import org.json.JSONObject

class TokenAuthenticator (
    private val context: Context,
    private val baseUrl: String
) : Authenticator {
    @Synchronized
    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.request.header("Authorization") == null) return null

        val path = response.request.url.encodedPath
        if (path.startsWith("/auth/signup/") ||
            path.startsWith("/auth/login/")  ||
            path.startsWith("/auth/refresh/")) {
            return null
        }

        val refresh = AuthManager.getRefreshToken(context) ?: return null

        val client = OkHttpClient()
        val json = JSONObject().apply { put("refreshToken", refresh) }.toString()
        val body = json.toRequestBody("application/json; charset=utf-8".toMediaType())

        val refreshReq = Request.Builder()
            .url("${baseUrl}auth/refresh")
            .post(body)
            .build()

        val refreshResp = runCatching { client.newCall(refreshReq).execute() }.getOrNull() ?: return null

        if (!refreshResp.isSuccessful) return null

        val payload = refreshResp.body?.string().orEmpty()
        val obj = runCatching { JSONObject(payload) }.getOrNull() ?: return null

        val newAccess = obj.optString("accessToken", "")
        val newRefresh = obj.optString("refreshToken", "")
        if (newAccess.isBlank()) return null

        AuthManager.saveTokens(
            context = context,
            access = newAccess,
            refresh = newRefresh.ifBlank { refresh }
        )

        return response.request.newBuilder()
            .removeHeader("Authorization").addHeader("Authorization", "Bearer $newAccess").build()
    }
}
