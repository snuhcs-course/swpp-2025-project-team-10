package com.example.librarytogether.network

import android.content.Context
import androidx.annotation.RawRes
import com.example.librarytogether.R
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Protocol
import okhttp3.Response
import okhttp3.ResponseBody.Companion.toResponseBody

class MockInterceptor(
    private val context: Context
) : Interceptor {

    private fun readJson(@RawRes id: Int): String =
        context.resources.openRawResource(id).bufferedReader().use { it.readText() }

    private fun makeResponse(req: okhttp3.Request, code: Int, body: String): Response =
        Response.Builder()
            .request(req)
            .protocol(Protocol.HTTP_1_1)
            .code(code)
            .message(if (code == 200) "OK" else "MOCK")
            .body(body.toResponseBody("application/json; charset=utf-8".toMediaType()))
            .build()

    override fun intercept(chain: Interceptor.Chain): Response {
        val req = chain.request()
        val path = req.url.encodedPath
        val method = req.method

        Thread.sleep(150)

        if (path.endsWith("/auth/login/") && method == "POST") {
            val body = readJson(R.raw.login_success)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/auth/signup/") && method == "POST") {
            val body = readJson(R.raw.signup_success)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/auth/forgot/start/") && method == "POST") {
            val body = readJson(R.raw.forgot_start_success)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/auth/forgot/verify/") && method == "POST") {
            val body = readJson(R.raw.forgot_verify_success)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/auth/forgot/reset/") && method == "POST") {
            val body = readJson(R.raw.forgot_reset_success)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/auth/token/refresh/") && method == "POST") {
            val body = """{
              "success": true,
              "data": { "accessToken": "ACCESS_VALID", "refreshToken": "REFRESH_VALID" }
            }"""
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/home/") && method == "GET") {
            val body = readJson(R.raw.home_feed)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/posts/12/like/") && method == "POST") {
            val body = readJson(R.raw.like)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/library/reviews/") && method == "GET") {
            val body = readJson(R.raw.my_feed)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/library/reviews/") && method == "GET") {
            val body = readJson(R.raw.my_feed)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/accounts/profile/me/") && method == "GET") {
            val body = readJson(R.raw.my_profile)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/accounts/profile/me/") && method == "PATCH") {
            val body = readJson(R.raw.my_profile)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/library/wishlist/") && method == "GET") {
            val body = readJson(R.raw.my_wishlist)
            return makeResponse(req, 200, body)
        }

        if (path.endsWith("/library/books/") && method == "GET") {
            val body = readJson(R.raw.my_books)
            return makeResponse(req, 200, body)
        }

        val notMocked = """{ "success": false, "error": { "code": "NOT_MOCKED", "message": "모킹 없음: $path" } }"""
        return makeResponse(req, 404, notMocked)
    }
}

