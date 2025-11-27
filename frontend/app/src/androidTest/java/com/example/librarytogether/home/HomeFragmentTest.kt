package com.example.librarytogether.feature.home

import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.RootMatchers.isDialog
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import com.google.android.material.R as MaterialR
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class HomeFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: HomeRepository = mock(HomeRepository::class.java)

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
    fun loadFeed_displaysPostInfo() {
        launchHomeFragment()

        onView(withId(R.id.rvFeed))
            .check(matches(isDisplayed()))

        onView(withText("테스트 책 제목")).check(matches(isDisplayed()))
        onView(withText("테스트 작가")).check(matches(isDisplayed()))
        onView(withText("테스트 유저")).check(matches(isDisplayed()))
        onView(withText("테스트 내용.")).check(matches(isDisplayed()))
    }

    private fun launchHomeFragment() {
        launchFragmentInHiltContainer<HomeFragment> {
        }
    }
}
