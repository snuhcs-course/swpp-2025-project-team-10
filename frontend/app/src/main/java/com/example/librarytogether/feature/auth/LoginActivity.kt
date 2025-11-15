package com.example.librarytogether.feature.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.EditText
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.BuildConfig
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.GoogleAuthRequest
import com.example.librarytogether.feature.auth.data.KakaoAuthRequest
import com.example.librarytogether.feature.auth.data.LoginRequest
import com.example.librarytogether.network.AuthManager
import com.example.librarytogether.network.RetrofitClient
import com.example.librarytogether.feature.main.MainActivity
import com.example.librarytogether.feature.onboarding.OnboardingActivity
import com.google.android.material.button.MaterialButton
import com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.kakao.sdk.user.UserApiClient
import kotlinx.coroutines.launch
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
            val sysBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(sysBars.left, sysBars.top, sysBars.right, sysBars.bottom)
            insets
        }

        email = findViewById(R.id.EmailText)
        password = findViewById(R.id.PasswordText)
        btnLogin = findViewById(R.id.LogInButton)
        btnForgot = findViewById(R.id.ForgotPasswordButton)
        btnGoogle = findViewById(R.id.GoogleLoginButton)
        btnKakao = findViewById(R.id.KakaoLoginButton)
        btnSignUp = findViewById(R.id.SignUpButton)
        credentialManager = CredentialManager.create(this)

        btnLogin.setOnClickListener { onClickLogin() }
        btnForgot.setOnClickListener { onClickForgotPassword() }
        btnSignUp.setOnClickListener { onClickSignUp() }
        btnKakao.setOnClickListener { onClickKakaoLogin() }
        btnGoogle.setOnClickListener { onClickGoogleLogin() }
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
                val resp = service.login(LoginRequest(username = id, password = pw))
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

                        val hasInitialTaste = body.user?.has_initial_taste ?: false
                        val next = if (hasInitialTaste) MainActivity::class.java else OnboardingActivity::class.java
                        startActivity(Intent(this@LoginActivity, next))
                        finish()
                    } else {
                        Toast.makeText(this@LoginActivity, "아이디 또는 비밀번호가 올바르지 않습니다.", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    when (resp.code()) {
                        400, 401, 403 ->
                            Toast.makeText(this@LoginActivity, "아이디와 비밀번호를 다시 확인해주세요.", Toast.LENGTH_SHORT).show()

                        in 500..599 ->
                            Toast.makeText(this@LoginActivity, "서버 오류. 잠시 후 다시 시도해주세요.", Toast.LENGTH_SHORT).show()

                        else ->
                            Toast.makeText(this@LoginActivity, "로그인 실패 (${resp.code()})", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.e("LoginActivity", "Login error: ${e.message}")
                Toast.makeText(this@LoginActivity, "네트워크 오류 발생. 잠시 후 다시 시도해주세요.", Toast.LENGTH_LONG).show()
            } finally {
                btnLogin.isEnabled = true
            }
        }
    }

    private fun onClickForgotPassword() {
        startActivity(Intent(this, ForgotPasswordActivity::class.java))
    }

    private fun onClickSignUp() {
        startActivity(Intent(this, SignupActivity::class.java))
    }

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

                            val hasTaste = body.user?.has_initial_taste ?: false
                            val next = if (hasTaste) MainActivity::class.java else OnboardingActivity::class.java
                            startActivity(Intent(this@LoginActivity, next))
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
        if (UserApiClient.instance.isKakaoTalkLoginAvailable(this)) {
            UserApiClient.instance.loginWithKakaoTalk(this) { token, error ->
                if (error != null) {
                    loginWithKakaoAccount()
                } else if (token != null) {
                    handleKakaoToken(token.accessToken)
                }
            }
        } else {
            loginWithKakaoAccount()
        }
    }

    private fun loginWithKakaoAccount() {
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
                val resp = service.kakaoLogin(KakaoAuthRequest(accessToken))
                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true && body.accessToken != null && body.refreshToken != null) {
                        AuthManager.saveTokens(
                            context = this@LoginActivity,
                            access = body.accessToken,
                            refresh = body.refreshToken
                        )

                        Toast.makeText(this@LoginActivity, "카카오 로그인 성공! 환영합니다", Toast.LENGTH_LONG).show()

                        val hasTaste = body.user?.has_initial_taste ?: false
                        val next = if (hasTaste) MainActivity::class.java else OnboardingActivity::class.java

                        startActivity(Intent(this@LoginActivity, next))
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
