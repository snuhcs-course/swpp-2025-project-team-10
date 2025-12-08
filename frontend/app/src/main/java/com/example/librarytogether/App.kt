package com.example.librarytogether

import android.app.Application
import com.kakao.sdk.common.KakaoSdk
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application() {
    override fun onCreate() {
        super.onCreate()

        try {
            KakaoSdk.init(this, BuildConfig.KAKAO_API_KEY)
        }
        catch (e: Exception){
        }
    }
}
