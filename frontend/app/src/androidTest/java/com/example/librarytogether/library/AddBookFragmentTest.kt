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
import org.hamcrest.Matchers.equalTo
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
            val recyclerView =
                requireView().findViewById<RecyclerView>(R.id.rvSearchResults)
            val adapter = recyclerView.adapter as SearchBookAdapter

            val dummyBook: Book = mock(Book::class.java).apply {
                `when`(title).thenReturn("테스트 도서 제목")
                `when`(authors).thenReturn(listOf("작가A", "작가B"))
                `when`(publisher).thenReturn("테스트 출판사")
                `when`(isbn).thenReturn("1234567890")
                `when`(publicationId).thenReturn("pub-id-1")
            }

            adapter.submitList(listOf(dummyBook))
        }

        onView(withId(R.id.rvSearchResults))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    click()
                )
            )

        onView(withId(R.id.etTitle))
            .check(matches(withText("테스트 도서 제목")))

        onView(withId(R.id.etAuthor))
            .check(matches(withText("작가A, 작가B")))

        onView(withId(R.id.etPublisher))
            .check(matches(withText("테스트 출판사")))

        onView(withId(R.id.etIsbn))
            .check(matches(withText("1234567890")))

        onView(withId(R.id.searchView))
            .check(matches(withEffectiveVisibility(Visibility.GONE)))
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
