package com.example.librarytogether.feature.auth

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.ForgotVerifyRequest
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

class VerifyEmailActivity : AppCompatActivity() {
    private lateinit var verify1: EditText
    private lateinit var verify2: EditText
    private lateinit var verify3: EditText
    private lateinit var verify4: EditText
    private lateinit var verify5: EditText
    private lateinit var verify6: EditText
    private lateinit var btnVerify: MaterialButton
    private lateinit var requestId: String
    private lateinit var email: String
    private val service: AuthApi by lazy {
        RetrofitClient.getClient(applicationContext).create(AuthApi::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.verify_email)
        requestId = intent.getStringExtra("requestId") ?: ""
        email = intent.getStringExtra("email") ?: ""

        verify1 = findViewById(R.id.VerifyNum1)
        verify2 = findViewById(R.id.VerifyNum2)
        verify3 = findViewById(R.id.VerifyNum3)
        verify4 = findViewById(R.id.VerifyNum4)
        verify5 = findViewById(R.id.VerifyNum5)
        verify6 = findViewById(R.id.VerifyNum6)
        btnVerify = findViewById(R.id.VerifyButton)

        setupVerifyInputs()
        btnVerify.setOnClickListener { onClickVerify() }
    }

    private fun setupVerifyInputs() {
        val inputs = listOf(verify1, verify2, verify3, verify4, verify5, verify6)

        for (i in inputs.indices) {
            inputs[i].addTextChangedListener(object : TextWatcher {
                override fun afterTextChanged(s: Editable?) {
                    if (s?.length == 1) {
                        if (i < inputs.lastIndex) inputs[i + 1].requestFocus()
                    }
                }

                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            })
        }
    }
    private fun onClickVerify() {
        val code = collectVerify()

        lifecycleScope.launch {
            try{
                val resp = service.forgotVerify(ForgotVerifyRequest(requestId, code))
                if (resp.isSuccessful) {
                    if (resp.body()?.ok == true) {
                        val intent = Intent(this@VerifyEmailActivity, ResetPasswordActivity::class.java)
                        startActivity(intent)
                    }
                }
                else {
                    Toast.makeText(this@VerifyEmailActivity, "서버 응답 없음", Toast.LENGTH_SHORT).show()
                }
            }
            catch (e: Exception) {
                Toast.makeText(this@VerifyEmailActivity, "네트워크 오류", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun collectVerify(): String {
        val inputs = listOf(verify1, verify2, verify3, verify4, verify5, verify6)
        return inputs.joinToString("") { it.text.toString().trim() }
    }

}