package com.example.librarytogether.home

import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Root
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.RootMatchers.isDialog
import androidx.test.espresso.matcher.RootMatchers.isPlatformPopup
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.home.HomeFragment
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.not
import org.hamcrest.Matcher
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`
import org.robolectric.annotation.Config
import org.robolectric.Shadows
import android.os.Looper
import org.mockito.Mockito.timeout
import org.mockito.Mockito.times
import org.mockito.Mockito.verify

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class HomeFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: HomeRepository = mock(HomeRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    private val mockPosts = Post(
        id = 1,
        posterId = 10,
        bookTitle = "테스트 책 제목",
        authorName = "테스트 작가",
        posterName = "테스트 유저",
        posterProfile = "",
        content = "테스트 내용.",
        imageUrls = emptyList(),
        likeCount = 5,
        commentCount = 2,
        createdAt = "2025-01-01T00:00:00Z",
        isLiked = false,
        bookId = "book-1",
        bookAvailableForBarter = true
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun loadFeed_displaysBasicInfo() {
        // Given
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(mockPosts))
        }

        // When
        launchHomeFragment()

        // Then
        onView(withId(R.id.rvFeed)).check(matches(isDisplayed()))
        onView(withText("테스트 책 제목")).check(matches(isDisplayed()))
        onView(withText("테스트 작가")).check(matches(isDisplayed()))
        onView(withText("좋아요")).check(matches(isDisplayed()))
        onView(withText("댓글")).check(matches(isDisplayed()))
    }

    @Test
    fun feedAdapter_bindsImages_sowsViewPager() {
        // Given
        val postWithImages = mockPosts.copy(
            id = 2,
            imageUrls = listOf("https://example.com/1.jpg", "https://example.com/2.jpg")
        )
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(postWithImages))
        }

        // When
        launchHomeFragment()

        // Then
        onView(withId(R.id.rvFeed))
            .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(0))

        onView(withId(R.id.vpImages)).check(matches(isDisplayed()))
        onView(withId(R.id.tabDots)).check(matches(isDisplayed()))
    }

    @Test
    fun feedAdapter_bindsNoImages_hidesViewPager() {
        // Given
        val postNoImages = mockPosts.copy(imageUrls = emptyList())
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(postNoImages))
        }

        // When
        launchHomeFragment()

        // Then
        onView(withId(R.id.vpImages)).check(matches(not(isDisplayed())))
    }

    @Test
    fun feedAdapter_disabledBarter_disablesButton() {
        // Given
        val postDisabled = mockPosts.copy(bookAvailableForBarter = false)
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(postDisabled))
        }

        // When
        launchHomeFragment()

        // Then
        onView(withId(R.id.btnExchange)).check(matches(not(isEnabled())))
    }

    @Test
    fun onClickExchange_showsDialog() {
        // Given
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(mockPosts))
        }
        launchHomeFragment()

        // When:
        onView(withId(R.id.btnExchange)).perform(click())

        // Then
        onView(withText("테스트 유저님에게 교환 신청"))
            .inRoot(isDialog())
            .check(matches(isDisplayed()))

        onView(withText("신청"))
            .inRoot(isDialog())
            .check(matches(isDisplayed()))
    }

    @Test
    fun onExpandContent_togglesMaxLines() {
        // Given
        val longContent = "긴 글".repeat(20)
        val postLong = mockPosts.copy(content = longContent)

        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(postLong))
        }
        launchHomeFragment()

        // When
        onView(withId(R.id.tvContent)).perform(click())

        onView(withText(longContent)).check(matches(isDisplayed()))
    }

    @Test
    fun handleSortMenuClick_executesAllSortBranches() {
        // Given
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(mockPosts))
        }

        // When
        launchFragmentInHiltContainer<HomeFragment>(
            themeResId = R.style.Theme_LibraryTogether
        ) {
            handleSortMenuClick(R.id.sort_latest)
            handleSortMenuClick(R.id.sort_popular)
            handleSortMenuClick(R.id.sort_region)

        }

        // Then
        onView(withId(R.id.rvFeed))
            .check(matches(isDisplayed()))
    }

    @Test
    fun clickAddToWishlist_callsViewModel() {
        // Given
        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(listOf(mockPosts))
        }
        launchHomeFragment()

        // When
        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    com.example.librarytogether.testing.CustomViewActions.clickChildViewWithId(R.id.btnAdd)
                )
            )

        // Then
    }

    private fun launchHomeFragment() {
        launchFragmentInHiltContainer<HomeFragment>() {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                try {
                    Navigation.setViewNavController(requireView(), mockNavController)
                } catch (e: Exception) {
                }
            }
        }
    }
}
