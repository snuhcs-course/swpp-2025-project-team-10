package com.example.librarytogether.feature.onboarding

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.librarytogether.R
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class OnboardingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, OnboardingFragment())
                .commit()
        }
    }
}
