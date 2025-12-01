package com.example.librarytogether.feature.library

import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import com.example.librarytogether.util.CustomViewActions
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class LibraryNavigationTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: LibraryRepository = mock(LibraryRepository::class.java)

    private val navController = mock(NavController::class.java)

    // --- Mock Data ---
    private val mockReviews = listOf(
        Review(
            id = 1, bookTitle = "review book", authorName = "author", userName = "name",
            userProfile = "", content = "contents", imageUrls = emptyList(),
            likeCount = 0, createdAt = "2025-01-01", isLiked = false
        )
    )
    private val mockBooks = listOf(
        Book(id = "book-1", title = "my book", authors = "author", cover_image = null, publisher = null, isbn = null)
    )
    private val mockWishlist = listOf(
        Book(id = "wish-1", title = "wish book", authors = "author", cover_image = null, publisher = null, isbn = null)
    )
    private val mockProfile = UserProfile(
        username = "Me", bio = "Bio", profileUrl = null,
        reviewCount = 1, followerCount = 0, followingCount = 0,
        favoriteGenres = listOf("R.string.genre_art_language"),
        preferences = UserPreferences(null, null, null, null, null, null, null, null, null)
    )

    @Before
    fun setup() {
        hiltRule.inject()

        runBlocking {
            `when`(mockRepo.getMyReviews()).thenReturn(mockReviews)
            `when`(mockRepo.getMyBooks()).thenReturn(mockBooks)
            `when`(mockRepo.getMyWishlist()).thenReturn(mockWishlist)
            `when`(mockRepo.getMyProfile()).thenReturn(mockProfile)
        }
    }

    @Test
    fun clickFab_inReviewTab_navigatesToWriteReview() {
        launchLibraryFragment()

        onView(withText("review book")).check(matches(isDisplayed()))

        onView(withId(R.id.fabAdd)).perform(click())

        verify(navController).navigate(R.id.action_libraryFragment_to_writeReviewFragment)
    }

    @Test
    fun clickBook_inBookTab_navigatesToBookDetail() {
        launchLibraryFragment()

        onView(withText(R.string.shelf)).perform(click())

        onView(withId(R.id.rvBooks))
            .check(matches(hasDescendant(withId(R.id.imgCover))))

        onView(withId(R.id.rvBooks))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    click()
                )
            )

        verify(navController).navigate(
            LibraryFragmentDirections.actionGlobalBookDetail(
                bookId = "book-1",
                source = EntrySource.BOOKSHELF
            )
        )
    }

    @Test
    fun clickFab_inBookTab_navigatesToAddBook() {
        launchLibraryFragment()

        onView(withText(R.string.shelf)).perform(click())

        onView(withId(R.id.fabAdd)).perform(click())

        verify(navController).navigate(
            LibraryFragmentDirections.actionLibraryFragmentToAddBookFragment(
                mode = AddBookMode.BOOKSHELF
            )
        )
    }

    @Test
    fun clickWishlist_inProfileTab_navigatesToBookDetail() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.rvWishlist))
            .perform(scrollTo())
            .check(matches(isDisplayed()))

        onView(withId(R.id.rvWishlist))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    click()
                )
            )

        verify(navController).navigate(
            LibraryFragmentDirections.actionGlobalBookDetail(
                bookId = "wish-1",
                source = EntrySource.WISHLIST
            )
        )
    }

    @Test
    fun clickEditProfile_togglesEditMode() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.fabAdd)).perform(click())

        onView(withId(R.id.editFavBook)).check(matches(isDisplayed()))
    }

    private fun launchLibraryFragment() {
        launchFragmentInHiltContainer<LibraryFragment> {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                if (viewLifecycleOwner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
        }
    }
}
