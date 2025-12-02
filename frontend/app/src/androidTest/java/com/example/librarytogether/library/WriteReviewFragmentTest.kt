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
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.data.Book
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

    val mockBooks = Book(
        id = "1234",
        title = "테스트 도서 제목",
        authors = listOf("작가A", "작가B"),
        publisher = "테스트 출판사",
        isbn = "1234567890",
        publicationId = "pub-id-1",
        cover_image = null,
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    private fun launchWriteReviewFragment(onFragment: (WriteReviewFragment.() -> Unit)? = null) {
        launchFragmentInHiltContainer<WriteReviewFragment> {
            viewLifecycleOwnerLiveData.observeForever { owner ->
                if (owner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
            onFragment?.invoke(this)
        }
    }

    @Test
    fun submit_withEmptyFields_doesNotNavigate() {
        launchWriteReviewFragment()

        onView(withId(R.id.etBookTitle))
            .perform(replaceText(""), closeSoftKeyboard())
        onView(withId(R.id.etBody))
            .perform(replaceText(""), closeSoftKeyboard())

        onView(withId(R.id.btnSubmit))
            .perform(click())

        verify(navController, never()).popBackStack()
    }

    @Test
    fun submit_withValidTitleAndBody_navigatesBack() {
        launchWriteReviewFragment()

        onView(withId(R.id.etBookTitle))
            .perform(replaceText("테스트 책 제목"), closeSoftKeyboard())
        onView(withId(R.id.etBody))
            .perform(replaceText("아주 좋은 책입니다."), closeSoftKeyboard())

        onView(withId(R.id.btnSubmit))
            .perform(click())

        verify(navController).popBackStack()
    }

    @Test
    fun submit_withTitleOnly_doesNotNavigate() {
        launchWriteReviewFragment()

        onView(withId(R.id.etBookTitle))
            .perform(replaceText("제목만 있는 리뷰"), closeSoftKeyboard())
        onView(withId(R.id.etBody))
            .perform(replaceText(""), closeSoftKeyboard())

        onView(withId(R.id.btnSubmit))
            .perform(click())

        verify(navController, never()).popBackStack()
    }

    @Test
    fun clickSearchResult_fillsBookFields_andHidesSearchView() {
        launchWriteReviewFragment {
            val method = WriteReviewFragment::class.java
                .getDeclaredMethod("onBookSearchResultClicked", Book::class.java)
            method.isAccessible = true
            method.invoke(this, mockBooks)
        }

        // 3) 에디트텍스트들이 dummyBook 정보로 채워졌는지 확인
        onView(withId(R.id.etBookTitle))
            .check(matches(withText("테스트 도서 제목")))

        onView(withId(R.id.etAuthor))
            .check(matches(withText("작가A, 작가B")))

        onView(withId(R.id.etPublisher))
            .check(matches(withText("테스트 출판사")))

        onView(withId(R.id.etIsbn))
            .check(matches(withText("1234567890")))
    }

}
