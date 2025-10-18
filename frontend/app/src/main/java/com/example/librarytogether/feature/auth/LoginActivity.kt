package com.example.librarytogether.feature.auth

import android.content.Intent
//import android.credentials.Credential
import android.os.Bundle
import android.widget.EditText
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.LoginRequest
import com.example.librarytogether.feature.auth.data.GoogleAuthRequest
import com.example.librarytogether.network.AuthManager
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch
import android.util.Log

// androidx.credentials import
import androidx.credentials.Credential
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetCredentialResponse
import androidx.credentials.exceptions.GetCredentialException
import com.example.librarytogether.BuildConfig
import com.example.librarytogether.feature.auth.data.KakaoAuthRequest
import com.example.librarytogether.feature.main.MainActivity

// Google ID Token 관련 import
import com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import com.kakao.sdk.user.UserApiClient
import dagger.hilt.android.HiltAndroidApp

// UUID
import java.util.UUID

class LoginActivity : AppCompatActivity() {

    private lateinit var email: EditText
    private lateinit var password: EditText
    private lateinit var btnLogin: MaterialButton
    private lateinit var btnForgot: MaterialButton
    private lateinit var btnGoogle: MaterialButton
    private lateinit var btnKakao: MaterialButton
    private lateinit var btnSignUp: MaterialButton
    private lateinit var credentialManager: CredentialManager


    companion object {
        // Google Cloud Console 에서 발급 받은 Web Client ID
        const val WEB_CLIENT_ID = BuildConfig.GOOGLE_API_KEY
    }
    private val service: AuthApi by lazy {
        RetrofitClient.getClient(applicationContext).create(AuthApi::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.log_in)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        email = findViewById(R.id.EmailText)
        password = findViewById(R.id.PasswordText)
        btnLogin = findViewById(R.id.LogInButton)
        btnForgot = findViewById(R.id.ForgotPasswordButton)
        btnGoogle = findViewById(R.id.GoogleLoginButton)
        btnKakao = findViewById(R.id.KakaoLoginButton)
        btnSignUp = findViewById(R.id.SignUpButton)

        btnLogin.setOnClickListener { onClickLogin() }
        btnForgot.setOnClickListener { onClickForgotPassword() }
        btnSignUp.setOnClickListener { onClickSignUp() }
        btnKakao.setOnClickListener { onClickKakaoLogin() }

        credentialManager = CredentialManager.create(this)
        btnGoogle.setOnClickListener {onClickGoogleLogin() }
    }

    private fun onClickLogin() {
        val id = email.text.toString().trim()
        val pw = password.text.toString()

        if (id.isEmpty() || pw.isEmpty()) {
            Toast.makeText(this, "아이디/비밀번호를 입력하세요", Toast.LENGTH_SHORT).show()
            return
        }

        btnLogin.isEnabled = false

        lifecycleScope.launch {
            try {
                val resp = service.login(LoginRequest(username=id, password=pw))

                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true) {
                        AuthManager.saveTokens(
                            context = this@LoginActivity,
                            access = body.accessToken,
                            refresh = body.refreshToken
                        )
                        Toast.makeText(this@LoginActivity, "로그인 성공!", Toast.LENGTH_SHORT).show()
                        email.setText("")
                        password.setText("")

                        startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                        finish()
                    }
                    else {
                        Toast.makeText(this@LoginActivity, "아이디 또는 비밀번호가 올바르지 않습니다.", Toast.LENGTH_SHORT).show()
                    }
                }
                else {
                    Toast.makeText(this@LoginActivity, "서버 응답 없음: ${resp.message()}", Toast.LENGTH_SHORT).show()
                }
            }
            catch (e: Exception) {
                Log.e("LoginActivity", "Login error: ${e.message}")
                Toast.makeText(this@LoginActivity, "네트워크 에러: ${e.message}", Toast.LENGTH_LONG).show()
            }
            finally {
                btnLogin.isEnabled = true
            }
        }
    }

    private fun onClickForgotPassword() {
        val intent = Intent(this, ForgotPasswordActivity::class.java)
        startActivity(intent)
    }

    private fun onClickSignUp() {
        val intent = Intent(this, SignupActivity::class.java)
        startActivity(intent)
    }

    //----------------------------------------------------------------------------------------------
    private fun onClickGoogleLogin() {
        val googleOption = GetSignInWithGoogleOption.Builder(WEB_CLIENT_ID)
            .setNonce(UUID.randomUUID().toString())
            .build()

        val request = GetCredentialRequest.Builder()
            .addCredentialOption(googleOption)
            .build()

        lifecycleScope.launch {
            try {
                val result = credentialManager.getCredential(this@LoginActivity, request)
                val credential = result.credential
                if (credential is CustomCredential &&
                    credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
                ) {
                    val googleCred = GoogleIdTokenCredential.createFrom(credential.data)
                    val idToken = googleCred.idToken

                    val resp = service.googleLogin(GoogleAuthRequest(idToken))
                    if (resp.isSuccessful) {
                        val body = resp.body()
                        if (body?.ok == true && body.accessToken != null && body.refreshToken != null) {
                            AuthManager.saveTokens(
                                context = this@LoginActivity,
                                access = body.accessToken,
                                refresh = body.refreshToken
                            )
                            Toast.makeText(
                                this@LoginActivity,
                                "구글 로그인 성공! ${googleCred.displayName}님 환영합니다",
                                Toast.LENGTH_LONG
                            ).show()
                             startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                             finish()
                        } else {
                            Toast.makeText(this@LoginActivity, body?.message ?: "로그인 실패", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@LoginActivity, "네트워크/로그인 에러", Toast.LENGTH_SHORT).show()
            }
        }
    }



    private fun onClickKakaoLogin() {
        // 카카오톡 앱 설치 여부 확인
        if(UserApiClient.instance.isKakaoTalkLoginAvailable(this)){
            // 앱 로그인
            UserApiClient.instance.loginWithKakaoTalk(this) { token, error ->
                if (error != null) {
                    // 카카오톡 앱 로그인 실패 -> 웹 계정 로그인으로 fallback
                    loginWithKakaoAccount()
                } else if (token != null) {
                    handleKakaoToken(token.accessToken)
                }
            }
        }else{
        // 앱이 없으면 웹 로그인
            loginWithKakaoAccount();
        }
    }
    private fun loginWithKakaoAccount(){
        UserApiClient.instance.loginWithKakaoAccount(this) { token, error ->
            if (error != null) {
                Toast.makeText(this, "카카오 로그인 실패: ${error.message}", Toast.LENGTH_SHORT).show()
            } else if (token != null) {
                handleKakaoToken(token.accessToken)
            }
        }
    }
    private fun handleKakaoToken(accessToken: String) {
        lifecycleScope.launch {
            try {
                val resp = service.kakaoLogin(KakaoAuthRequest(accessToken)) // 로그인 API 호출
                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true && body.accessToken != null && body.refreshToken != null) {
                        AuthManager.saveTokens(
                            context = this@LoginActivity,
                            access = body.accessToken,
                            refresh = body.refreshToken
                        )
                        Toast.makeText(this@LoginActivity, "카카오 로그인 성공! 환영합니다", Toast.LENGTH_LONG).show()
                         startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                         finish()
                    } else {
                        Toast.makeText(this@LoginActivity, body?.message ?: "로그인 실패", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(this@LoginActivity, "서버 로그인 실패", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@LoginActivity, "네트워크 에러", Toast.LENGTH_SHORT).show()
            }
        }
    }

}
