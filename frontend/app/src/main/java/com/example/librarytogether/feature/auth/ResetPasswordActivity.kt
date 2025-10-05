package com.example.librarytogether.feature.auth

import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.ForgotResetRequest
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

class ResetPasswordActivity : AppCompatActivity() {
    private lateinit var newPassword: EditText
    private lateinit var btnReset: MaterialButton
    private val service: AuthApi by lazy {
        RetrofitClient.getClient(applicationContext).create(AuthApi::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.reset_password)

        newPassword = findViewById(R.id.PasswordText)
        btnReset = findViewById(R.id.ResetPasswordButton)

        btnReset.setOnClickListener { onClickSignUp() }
    }

    private fun onClickSignUp() {
        val pw = newPassword.text.toString()

        if (pw.isEmpty()) {
            Toast.makeText(this, "모든 필드를 입력하세요", Toast.LENGTH_SHORT).show()
            return
        }
        val passwordRegex = Regex("^(?=.*[A-Za-z]).{6,}$")
        if(!pw.matches(passwordRegex)){
            Toast.makeText(this, "비밀번호는 6자 이상 영문을 포함해야 합니다", Toast.LENGTH_SHORT).show()
            return
        }

        btnReset.isEnabled = false

        lifecycleScope.launch {
            try {
                val resp = service.forgotReset(ForgotResetRequest(pw))

                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true) {
                        newPassword.setText("")
                        val intent = Intent(this@ResetPasswordActivity, LoginActivity::class.java)
                        startActivity(intent)
                    }
                    else {
                        Toast.makeText(this@ResetPasswordActivity, "모든 필드를 올바르게 입력하세요", Toast.LENGTH_SHORT).show()
                    }
                }
                else {
                    Toast.makeText(this@ResetPasswordActivity, "서버 응답 없음", Toast.LENGTH_SHORT).show()
                }
            }
            catch (e: Exception) {
                Toast.makeText(this@ResetPasswordActivity, "네트워크 에러", Toast.LENGTH_SHORT).show()
            }
            finally {
                btnReset.isEnabled = true
            }
        }
    }
}