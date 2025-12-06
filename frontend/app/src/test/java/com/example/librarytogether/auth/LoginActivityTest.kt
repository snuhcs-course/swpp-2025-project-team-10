package com.example.librarytogether.feature.auth

import android.app.Activity
import android.content.Intent
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.intent.Intents
import androidx.test.espresso.intent.matcher.IntentMatchers.hasComponent
import androidx.test.espresso.matcher.RootMatchers.withDecorView
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.LoginRequest
import com.example.librarytogether.feature.auth.data.LoginResponse
import com.example.librarytogether.feature.auth.data.UserInfo
import com.example.librarytogether.feature.main.MainActivity
import com.example.librarytogether.feature.onboarding.OnboardingActivity
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.`is`
import org.hamcrest.CoreMatchers.not
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito
import org.mockito.Mockito.*
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowToast
import retrofit2.Response

@RunWith(AndroidJUnit4::class)
@Config(sdk = [34]) // SDK 버전 명시
class LoginActivityTest {

    private val mockApi: AuthApi = mock(AuthApi::class.java)

    @Before
    fun setup() {
        Intents.init()
    }

    @After
    fun tearDown() {
        Intents.release()
    }

    private fun <T> any(type: Class<T>): T = Mockito.any(type)

    @Test
    fun login_success_navigatesToMainActivity() {
        // Given
        val successResponse = LoginResponse(
            ok = true,
            accessToken = "acc",
            refreshToken = "ref",
            user = UserInfo(1, "u", "e", has_initial_taste = true)
        )

        runBlocking {
            // [수정 포인트] any() 대신 any(Class) ?: DummyObject 사용
            `when`(mockApi.login(any(LoginRequest::class.java) ?: LoginRequest("", "")))
                .thenReturn(Response.success(successResponse))
        }

        val scenario = ActivityScenario.launch(LoginActivity::class.java)
        scenario.onActivity { replaceAuthApi(it, mockApi) }

        // When
        onView(withId(R.id.EmailText)).perform(typeText("test@test.com"), closeSoftKeyboard())
        onView(withId(R.id.PasswordText)).perform(typeText("password"), closeSoftKeyboard())
        onView(withId(R.id.LogInButton)).perform(click())

        // Then
        runBlocking {
            verify(mockApi).login(any(LoginRequest::class.java) ?: LoginRequest("", ""))
        }
        Intents.intended(hasComponent(MainActivity::class.java.name))
        scenario.close()
    }

    @Test
    fun login_success_noTaste_navigatesToOnboarding() {
        // Given
        val noTasteUser = LoginResponse(
            ok = true, "a", "r",
            user = UserInfo(1, "u", "e", has_initial_taste = false)
        )
        runBlocking {
            `when`(mockApi.login(any(LoginRequest::class.java) ?: LoginRequest("", "")))
                .thenReturn(Response.success(noTasteUser))
        }

        val scenario = ActivityScenario.launch(LoginActivity::class.java)
        scenario.onActivity { replaceAuthApi(it, mockApi) }

        // When
        onView(withId(R.id.EmailText)).perform(typeText("u"), closeSoftKeyboard())
        onView(withId(R.id.PasswordText)).perform(typeText("p"), closeSoftKeyboard())
        onView(withId(R.id.LogInButton)).perform(click())

        // Then
        Intents.intended(hasComponent(OnboardingActivity::class.java.name))
        scenario.close()
    }

    @Test
    fun login_failure_showsToast() {
        // Given
        runBlocking {
            val errorBody = okhttp3.ResponseBody.create(null, "")
            `when`(mockApi.login(any(LoginRequest::class.java) ?: LoginRequest("", "")))
                .thenReturn(Response.error(401, errorBody))
        }

        val scenario = ActivityScenario.launch(LoginActivity::class.java)
        scenario.onActivity { replaceAuthApi(it, mockApi) }

        // When
        onView(withId(R.id.EmailText)).perform(typeText("u"), closeSoftKeyboard())
        onView(withId(R.id.PasswordText)).perform(typeText("p"), closeSoftKeyboard())
        onView(withId(R.id.LogInButton)).perform(click())

        // Then: Espresso 대신 ShadowToast 사용
        val latestToastText = ShadowToast.getTextOfLatestToast()
        assertEquals("아이디와 비밀번호를 다시 확인해주세요.", latestToastText)

        scenario.close()
    }


    @Test
    fun clickSignUp_navigatesToSignupActivity() {
        ActivityScenario.launch(LoginActivity::class.java).use {
            onView(withId(R.id.SignUpButton)).perform(click())
            Intents.intended(hasComponent(SignupActivity::class.java.name))
        }
    }

    private fun replaceAuthApi(activity: Activity, mock: AuthApi) {
        val field = LoginActivity::class.java.getDeclaredField("service\$delegate")
        field.isAccessible = true
        val lazyValue = field.get(activity)
        val valueField = lazyValue.javaClass.getDeclaredField("_value")
        valueField.isAccessible = true
        valueField.set(lazyValue, mock)
    }
}
