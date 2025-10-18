package com.example.librarytogether.network

import java.util.concurrent.TimeUnit
import android.content.Context
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object MockConfig {
    // 필요할 때만 true로
    const val USE_MOCK = true
    // JWT 흐름까지 테스트할 건지
    const val TEST_JWT_FLOW = true
}

object RetrofitClient {
    // Use 192.0.0.2 for physical device on same network
    // Use 10.0.2.2 for emulator
    private const val BASE_URL = "http://192.0.0.2:8000/"

    @Volatile
    private var retrofit: Retrofit? = null

    fun getClient(context: Context): Retrofit {
        retrofit?.let { return it }

        synchronized(this) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            val okHttp: OkHttpClient = OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(20, TimeUnit.SECONDS)
                .writeTimeout(20, TimeUnit.SECONDS)
                .apply {
                    addInterceptor(logging)
                    if (MockConfig.USE_MOCK) {
                        if (MockConfig.TEST_JWT_FLOW) {
                            addInterceptor(AuthInterceptor(context.applicationContext))
                        }
                        addInterceptor(MockInterceptor(context.applicationContext))
                        if (MockConfig.TEST_JWT_FLOW) {
                            authenticator(TokenAuthenticator(context.applicationContext, BASE_URL))
                        }
                    } else {
                        addInterceptor(AuthInterceptor(context.applicationContext))
                        authenticator(TokenAuthenticator(context.applicationContext, BASE_URL))
                    }
                }
                .build()

            val built = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(okHttp)
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            retrofit = built
            return built
        }
    }
}
