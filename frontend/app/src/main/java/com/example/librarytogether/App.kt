package com.example.librarytogether

import android.app.Application
import com.kakao.sdk.common.KakaoSdk

class App : Application() {
    override fun onCreate() {
        super.onCreate()

        // Kakao SDK 초기화
        //노출 위험 있음. 원하면 수정할 것.
        KakaoSdk.init(this, "dd8a497c4db87c8907318022920a405c")
    }
}