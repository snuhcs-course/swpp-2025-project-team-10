package com.example.librarytogether.feature.explore

import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.explore.data.ExploreRepository
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.not
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class ExploreFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: ExploreRepository = mock(ExploreRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    private val mockBook = Book(
        id = "test-book-id",
        title = "테스트 책 제목",
        authors = listOf("테스트 작가"),
        cover_image = "https://example.com/cover.jpg",
        publisher = "테스트 출판사",
        isbn = "123456789",
        publicationId = "pub-001"
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun loadRecommendations_displaysData() {
        // Given
        runBlocking {
            `when`(mockRepo.getRecommendations()).thenReturn(listOf(mockBook))
        }

        // When
        launchExploreFragment()

        // Then
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvEmpty)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvError)).check(matches(not(isDisplayed())))

        onView(withId(R.id.listRecommendations)).check(matches(isDisplayed()))

        onView(withText("테스트 책 제목")).check(matches(isDisplayed()))
        onView(withText("테스트 작가")).check(matches(isDisplayed()))
    }

    @Test
    fun loadRecommendations_showsEmptyState() {
        // Given
        runBlocking {
            `when`(mockRepo.getRecommendations()).thenReturn(emptyList())
        }

        // When
        launchExploreFragment()

        // Then
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
        onView(withId(R.id.listRecommendations)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvError)).check(matches(not(isDisplayed())))

        onView(withId(R.id.tvEmpty)).check(matches(isDisplayed()))
    }

    @Test
    fun loadRecommendations_showsErrorState() {
        // Given
        val errorMessage = "네트워크 오류 발생"
        runBlocking {
            `when`(mockRepo.getRecommendations()).thenThrow(RuntimeException(errorMessage))
        }

        // When
        launchExploreFragment()

        // Then
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
        onView(withId(R.id.listRecommendations)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvEmpty)).check(matches(not(isDisplayed())))

        onView(withId(R.id.tvError)).check(matches(isDisplayed()))
        onView(withText(errorMessage)).check(matches(isDisplayed()))
    }

    @Test
    fun clickItem_navigatesToDetail() {
        // Given
        runBlocking {
            `when`(mockRepo.getRecommendations()).thenReturn(listOf(mockBook))
        }
        launchExploreFragment()

        // When
        onView(withId(R.id.listRecommendations))
            .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

        // Then
        val expectedDirection = BookDetailFragmentDirections.actionGlobalBookDetail(
            bookId = mockBook.id,
            source = EntrySource.EXPLORE
        )
        verify(mockNavController).navigate(expectedDirection)
    }

    private fun launchExploreFragment() {
        launchFragmentInHiltContainer<ExploreFragment> {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                try {
                    Navigation.setViewNavController(requireView(), mockNavController)
                } catch (e: Exception) {
                }
            }
        }
    }
}
