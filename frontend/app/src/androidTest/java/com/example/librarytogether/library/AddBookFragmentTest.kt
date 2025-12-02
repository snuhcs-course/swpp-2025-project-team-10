package com.example.librarytogether.library


import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.AddBookFragment
import com.example.librarytogether.feature.library.SearchBookAdapter
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.`when`
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.verify

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class AddBookFragmentTest {

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

    private fun launchAddBookFragment(onFragment: (AddBookFragment.() -> Unit)? = null) {
        launchFragmentInHiltContainer<AddBookFragment> {
            viewLifecycleOwnerLiveData.observeForever { owner ->
                if (owner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
            onFragment?.invoke(this)
        }
    }

    @Test
    fun clickSearchResult_fillsFields_andHidesSearchView() {
        launchAddBookFragment {
            val method = AddBookFragment::class.java
                .getDeclaredMethod("onBookSearchResultClicked", Book::class.java)
            method.isAccessible = true
            method.invoke(this, mockBooks)
        }


        onView(withId(R.id.etTitle))
            .check(matches(withText("테스트 도서 제목")))

        onView(withId(R.id.etAuthor))
            .check(matches(withText("작가A, 작가B")))

        onView(withId(R.id.etPublisher))
            .check(matches(withText("테스트 출판사")))

        onView(withId(R.id.etIsbn))
            .check(matches(withText("1234567890")))
    }

    @Test
    fun saveWithoutSelectingBook_doesNotNavigate() {
        launchAddBookFragment()

        onView(withId(R.id.btnSaveBook))
            .perform(click())

        verify(navController, never()).popBackStack()

         onView(withText("먼저 검색 결과에서 책을 선택해 주세요."))
             .check(matches(isDisplayed()))
    }
}
