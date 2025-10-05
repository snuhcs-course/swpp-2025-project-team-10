package com.example.librarytogether.feature.auth

import android.content.Intent
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
import com.example.librarytogether.feature.auth.data.SignUpRequest
import com.example.librarytogether.feature.auth.data.SignUpResponse
import com.example.librarytogether.feature.auth.data.GoogleAuthRequest
import com.example.librarytogether.network.AuthManager
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

// androidx.credentials import
import androidx.credentials.Credential
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetCredentialResponse
import androidx.credentials.exceptions.GetCredentialException
import com.example.librarytogether.feature.auth.data.KakaoAuthRequest

// Google ID Token 관련 import
import com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import com.kakao.sdk.user.UserApiClient

// UUID
import java.util.UUID


class SignupActivity : AppCompatActivity() {

    private lateinit var userName: EditText
    private lateinit var email: EditText
    private lateinit var password: EditText
    private lateinit var btnSignUp: MaterialButton
    private lateinit var btnGoogle: MaterialButton
    private lateinit var btnKakao: MaterialButton
    private lateinit var btnLogin: MaterialButton

    private val service: AuthApi by lazy {
        RetrofitClient.getClient(applicationContext).create(AuthApi::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.sign_up)

        // View binding
        userName = findViewById(R.id.UserNameText)
        email = findViewById(R.id.EmailText)
        password = findViewById(R.id.PasswordText)
        btnSignUp = findViewById(R.id.SignUpButton)
        btnGoogle = findViewById(R.id.GoogleSignUpButton)
        btnKakao = findViewById(R.id.KakaoLoginButton)
        btnLogin = findViewById(R.id.LogInButton)

        // Button click handler
        btnSignUp.setOnClickListener { onClickSignUp() }
        btnGoogle.setOnClickListener { onClickGoogleSignUp() }
        btnKakao.setOnClickListener { onClickKakaoSignUp() }
        btnLogin.setOnClickListener { onClickGoToLogin() }
    }

    private fun onClickSignUp() {
        val id = userName.text.toString().trim()
        val mail = email.text.toString().trim()
        val pw = password.text.toString()

        if (id.isEmpty() || mail.isEmpty() || pw.isEmpty()) {
            Toast.makeText(this, "모든 필드를 입력하세요", Toast.LENGTH_SHORT).show()
            return
        }
        val passwordRegex = Regex("^(?=.*[A-Za-z]).{6,}$")
        if(!pw.matches(passwordRegex)){
            Toast.makeText(this, "비밀번호는 6자 이상 영문을 포함해야 합니다", Toast.LENGTH_SHORT).show()
            return
        }

        btnSignUp.isEnabled = false


        lifecycleScope.launch {
            try {
                val resp = service.signUp(SignUpRequest(username=id, password=pw, email=mail))

                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true) {
                        Toast.makeText(this@SignupActivity, "회원가입 성공! 로그인해주세요.", Toast.LENGTH_LONG).show()
                        // Reset input fields(입력 초기화)
                        userName.setText("")
                        email.setText("")
                        password.setText("")

                        // TODO: Navigate to HomeActivity when implemented
                        // For now, return to login screen after successful signup
                        finish()
                    }
                    else {
                        Toast.makeText(this@SignupActivity, "회원가입 실패: ${body?.message ?: "알 수 없는 오류"}", Toast.LENGTH_SHORT).show()
                    }
                }
                else {
                    // Handle error response - show specific error message
                    val errorMessage = when (resp.code()) {
                        400 -> {
                            // Try to parse error body for specific validation errors
                            try {
                                val errorBody = resp.errorBody()?.string()
                                if (errorBody?.contains("already exists") == true) {
                                    "이미 사용 중인 아이디 또는 이메일입니다"
                                } else if (errorBody?.contains("Password") == true) {
                                    "비밀번호가 요구사항을 충족하지 않습니다"
                                } else {
                                    "입력 정보를 확인해주세요"
                                }
                            } catch (e: Exception) {
                                "입력 정보를 확인해주세요"
                            }
                        }
                        500 -> "서버 오류가 발생했습니다"
                        else -> "회원가입 실패: ${resp.message()}"
                    }
                    Toast.makeText(this@SignupActivity, errorMessage, Toast.LENGTH_LONG).show()
                }
            }
            catch (e: Exception) {
                Toast.makeText(this@SignupActivity, "네트워크 에러: ${e.message}", Toast.LENGTH_SHORT).show()
            }
            finally {
                btnSignUp.isEnabled = true
            }
        }
    }

    private fun onClickGoogleSignUp() {
        val googleOption = GetSignInWithGoogleOption.Builder(LoginActivity.WEB_CLIENT_ID)
            .setNonce(UUID.randomUUID().toString())
            .build()

        val request = GetCredentialRequest.Builder()
            .addCredentialOption(googleOption)
            .build()

        lifecycleScope.launch {
            try {
                val result = CredentialManager.create(this@SignupActivity)
                    .getCredential(this@SignupActivity, request)

                val credential = result.credential
                if (credential is CustomCredential &&
                    credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
                ) {
                    val googleCred = GoogleIdTokenCredential.createFrom(credential.data)
                    val idToken = googleCred.idToken

                    val resp = service.googleSignup(GoogleAuthRequest(idToken))
                    if (resp.isSuccessful) {
                        val body = resp.body()
                        if (body?.ok == true && body.accessToken != null && body.refreshToken != null) {
                            AuthManager.saveTokens(
                                context = this@SignupActivity,
                                access = body.accessToken,
                                refresh = body.refreshToken
                            )
                            Toast.makeText(
                                this@SignupActivity,
                                "구글 계정 회원가입 성공! ${googleCred.displayName}님 환영합니다",
                                Toast.LENGTH_LONG
                            ).show()
                            // TODO: Navigate to HomeActivity when implemented
                            // startActivity(Intent(this@SignupActivity, HomeActivity::class.java))
                            // finish()
                        } else {
                            Toast.makeText(this@SignupActivity, body?.message ?: "회원가입 실패", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@SignupActivity, "네트워크/로그인 에러: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }


    // 카카오 릴리지용 key hash 발급 및 등록 아직 안함.
    private fun onClickKakaoSignUp() {
        UserApiClient.instance.loginWithKakaoTalk(this) { token, error ->
            if (error != null) {
                loginWithKakaoAccountForSignup()
            } else if (token != null) {
                handleKakaoSignup(token.accessToken)
            }
        }
    }

    private fun loginWithKakaoAccountForSignup() {
        UserApiClient.instance.loginWithKakaoAccount(this) { token, error ->
            if (error != null) {
                Toast.makeText(this, "카카오 회원가입 실패: ${error.message}", Toast.LENGTH_SHORT).show()
            } else if (token != null) {
                handleKakaoSignup(token.accessToken)
            }
        }
    }

    private fun handleKakaoSignup(accessToken: String) {
        lifecycleScope.launch {
            try {
                val resp = service.kakaoSignup(KakaoAuthRequest(accessToken))
                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.ok == true && body.accessToken != null && body.refreshToken != null) {
                        AuthManager.saveTokens(
                            context = this@SignupActivity,
                            access = body.accessToken,
                            refresh = body.refreshToken
                        )
                        Toast.makeText(this@SignupActivity, "카카오 회원가입 성공! 환영합니다", Toast.LENGTH_LONG).show()
                        // TODO: Navigate to HomeActivity when implemented
                        // startActivity(Intent(this@SignupActivity, HomeActivity::class.java))
                        // finish()
                    } else {
                        Toast.makeText(this@SignupActivity, body?.message ?: "회원가입 실패", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@SignupActivity, "네트워크 에러: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }


    private fun onClickGoToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        startActivity(intent)
        finish()
    }
}
