package com.example.librarytogether.feature.auth

import android.app.Activity
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.auth.data.AuthApi
import com.example.librarytogether.feature.auth.data.SignUpRequest
import com.example.librarytogether.feature.auth.data.SignUpResponse
import kotlinx.coroutines.runBlocking
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
@Config(sdk = [34], qualifiers = "xlarge")
class SignupActivityTest {

    private val mockApi: AuthApi = mock(AuthApi::class.java)

    @Before
    fun setup() {
    }

    private fun <T> any(type: Class<T>): T = Mockito.any(type)

    @Test
    fun signup_emptyInput_showsWarning() {
        val scenario = ActivityScenario.launch(SignupActivity::class.java)

        onView(withId(R.id.SignUpButton)).perform(click())

        assertEquals("모든 필드를 입력하세요", ShadowToast.getTextOfLatestToast())

        scenario.close()
    }

    @Test
    fun signup_invalidPassword_showsWarning() {
        val scenario = ActivityScenario.launch(SignupActivity::class.java)

        onView(withId(R.id.UserNameText)).perform(typeText("user"), closeSoftKeyboard())
        onView(withId(R.id.EmailText)).perform(typeText("a@a.com"), closeSoftKeyboard())
        onView(withId(R.id.PasswordText)).perform(typeText("1234"), closeSoftKeyboard())

        onView(withId(R.id.SignUpButton)).perform(click())

        assertEquals("비밀번호는 8자 이상 영문을 포함해야 합니다", ShadowToast.getTextOfLatestToast())

        scenario.close()
    }

    @Test
    fun signup_success_showsToastAndFinishes() {
        // Given
        runBlocking {
            val response = SignUpResponse(ok = true, message = "success")
            val dummyRequest = SignUpRequest("", "", "")
            `when`(mockApi.signUp(any(SignUpRequest::class.java) ?: dummyRequest))
                .thenReturn(Response.success(response))
        }

        val scenario = ActivityScenario.launch(SignupActivity::class.java)
        scenario.onActivity { replaceAuthApi(it, mockApi) }

        // When
        onView(withId(R.id.UserNameText)).perform(typeText("user"), closeSoftKeyboard())
        onView(withId(R.id.EmailText)).perform(typeText("a@a.com"), closeSoftKeyboard())
        onView(withId(R.id.PasswordText)).perform(typeText("password123"), closeSoftKeyboard())

        onView(withId(R.id.SignUpButton)).perform(click())

        // Then
        runBlocking {
            val dummyRequest = SignUpRequest("", "", "")
            verify(mockApi).signUp(any(SignUpRequest::class.java) ?: dummyRequest)
        }

        assertEquals("회원가입 성공! 로그인해주세요.", ShadowToast.getTextOfLatestToast())

        scenario.onActivity { activity ->
            assert(activity.isFinishing)
        }
        scenario.close()
    }

    private fun replaceAuthApi(activity: Activity, mock: AuthApi) {
        val field = SignupActivity::class.java.getDeclaredField("service\$delegate")
        field.isAccessible = true
        val lazyValue = field.get(activity)
        val valueField = lazyValue.javaClass.getDeclaredField("_value")
        valueField.isAccessible = true
        valueField.set(lazyValue, mock)
    }
}
