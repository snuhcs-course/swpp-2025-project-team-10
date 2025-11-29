package com.example.librarytogether.feature.library

import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.Visibility
import androidx.test.espresso.matcher.ViewMatchers.withEffectiveVisibility
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.verify

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class WriteReviewFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: LibraryRepository = mock(LibraryRepository::class.java)

    private val navController: NavController = mock(NavController::class.java)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    private fun launchWriteReviewFragment() {
        launchFragmentInHiltContainer<WriteReviewFragment> {
            viewLifecycleOwnerLiveData.observeForever { owner ->
                if (owner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
        }
    }

    @Test
    fun submit_withEmptyFields_doesNotNavigate() {
        launchWriteReviewFragment()

        // 제목/내용 비우기
        onView(withId(R.id.etBookTitle))
            .perform(replaceText(""), closeSoftKeyboard())
        onView(withId(R.id.etBody))
            .perform(replaceText(""), closeSoftKeyboard())

        // btnSubmit 은 NestedScrollView 밖에 있어서 scrollTo() 금지
        onView(withId(R.id.btnSubmit))
            .perform(click())

        // 실패 상태라 popBackStack 이 호출되면 안 됨
        verify(navController, never()).popBackStack()
    }

    @Test
    fun submit_withValidTitleAndBody_navigatesBack() {
        launchWriteReviewFragment()

        onView(withId(R.id.etBookTitle))
            .perform(replaceText("테스트 책 제목"), closeSoftKeyboard())
        onView(withId(R.id.etBody))
            .perform(replaceText("아주 좋은 책입니다."), closeSoftKeyboard())

        // 여기서도 scrollTo() 없이 클릭
        onView(withId(R.id.btnSubmit))
            .perform(click())

        // 성공 시 뒤로 가기
        verify(navController).popBackStack()
    }
}
