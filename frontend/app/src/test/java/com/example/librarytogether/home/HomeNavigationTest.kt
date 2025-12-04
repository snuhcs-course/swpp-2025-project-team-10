package com.example.librarytogether.feature.home

import android.os.Looper
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.RootMatchers.isDialog
import androidx.test.espresso.matcher.ViewMatchers.assertThat
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.feature.search.SearchSharedViewModel
import com.example.librarytogether.testing.CustomViewActions
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.Matchers.equalTo
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.robolectric.Shadows
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class HomeNavigationTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: HomeRepository = mock(HomeRepository::class.java)

    private val navController = mock(NavController::class.java)

    private val mockPosts = listOf(
        Post(
            id = 1,
            posterId = 10,
            bookTitle = "테스트 책 제목",
            authorName = "테스트 작가",
            posterName = "테스트 유저",
            posterProfile = "",
            content = "테스트 내용.",
            imageUrls = emptyList(),
            likeCount = 5,
            commentCount = 0,
            createdAt = "2025-01-01T00:00:00Z",
            isLiked = false,
            bookId = "book-1",
            bookAvailableForBarter = true
        )
    )

    @Before
    fun setup() {
        hiltRule.inject()

        runBlocking {
            `when`(mockRepo.getFeed()).thenReturn(mockPosts)
        }
    }

    @Test
    fun clickProfile_navigatesToUserProfile() {
        launchHomeFragment()

        onView(withText("테스트 책 제목")).check(matches(isDisplayed()))

        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    CustomViewActions.clickChildViewWithId(R.id.ivProfileImage)
                )
            )

        verify(navController).navigate(
            HomeFragmentDirections.actionGlobalToUserProfileFragment(userId = 10)
        )
    }

    @Test
    fun clickUserName_navigatesToUserProfile() {
        launchHomeFragment()

        onView(withText("테스트 유저")).check(matches(isDisplayed()))

        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    CustomViewActions.clickChildViewWithId(R.id.tvPoster)
                )
            )

        verify(navController).navigate(
            HomeFragmentDirections.actionGlobalToUserProfileFragment(userId = 10)
        )
    }

    @Test
    fun clickExchange_showsDialog() {
        launchHomeFragment()

        onView(withText("테스트 책 제목")).check(matches(isDisplayed()))

        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    CustomViewActions.clickChildViewWithId(R.id.btnExchange)
                )
            )

        // Dialog가 뜨는 시간을 고려하여 UI 스레드를 대기시킬 필요가 있을 경우 사용
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        onView(withText("취소"))
            .inRoot(isDialog())
            .check(matches(isDisplayed()))
    }

    @Test
    fun clickTitle_setsSearchQuery_andSelectsSearchTab() {
        lateinit var searchVm: SearchSharedViewModel

        launchFragmentInHiltContainer<HomeFragment>(
            themeResId = R.style.Theme_LibraryTogether
        ) {
            searchVm = ViewModelProvider(requireActivity())[SearchSharedViewModel::class.java]
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                if (viewLifecycleOwner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
        }

        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    CustomViewActions.clickChildViewWithId(R.id.tvTitle)
                )
            )

        assertThat(
            searchVm.pendingQuery.value,
            equalTo(mockPosts.first().bookTitle)
        )
    }

    @Test
    fun clickAuthor_setsSearchQuery_andSelectsSearchTab() {
        lateinit var searchVm: SearchSharedViewModel

        launchFragmentInHiltContainer<HomeFragment>(
            themeResId = R.style.Theme_LibraryTogether
        ) {
            searchVm = ViewModelProvider(requireActivity())[SearchSharedViewModel::class.java]
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                if (viewLifecycleOwner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
        }

        onView(withId(R.id.rvFeed))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    CustomViewActions.clickChildViewWithId(R.id.tvAuthor)
                )
            )

        assertThat(
            searchVm.pendingQuery.value,
            equalTo(mockPosts.first().authorName)
        )
    }

    private fun launchHomeFragment() {
        launchFragmentInHiltContainer<HomeFragment> {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                if (viewLifecycleOwner != null) {
                    Navigation.setViewNavController(requireView(), navController)
                }
            }
        }
    }
}
