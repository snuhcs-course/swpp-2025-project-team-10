package com.example.librarytogether.feature.auth

import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.ForgotPasswordRequest
import com.example.librarytogether.feature.auth.data.ForgotPasswordResponse
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

class ForgotPasswordActivity : AppCompatActivity() {
    private lateinit var email: EditText
    private lateinit var btnSendEmail: MaterialButton
    private val service: AuthApi by lazy {
        RetrofitClient.getClient(applicationContext).create(AuthApi::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.forgot_password)

        email = findViewById(R.id.EmailText)
        btnSendEmail = findViewById(R.id.SendVerifyButton)

        btnSendEmail.setOnClickListener { onClickSendEmail() }
    }

    private fun onClickSendEmail() {
        val address = email.text.toString().trim()

        if (address.isEmpty()) {
            Toast.makeText(this, "이메일을 입력하세요", Toast.LENGTH_SHORT).show()
            return
        }

        lifecycleScope.launch {
            try {
                val resp = service.forgotPassword(ForgotPasswordRequest(address))
                if (resp.isSuccessful) {
                    val requestId = resp.body()?.requestId
                    val intent = Intent(this@ForgotPasswordActivity, VerifyEmailActivity::class.java)
                        .putExtra("email", address)
                        .putExtra("requestId", requestId)
                    startActivity(intent)
                } else {
                    Toast.makeText(this@ForgotPasswordActivity, "서버 응답 없음", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@ForgotPasswordActivity, "네트워크 오류", Toast.LENGTH_SHORT).show()
            }
        }
    }
}