package com.example.librarytogether.feature.library

import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.action.ViewActions.typeText
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.Matchers.not
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`
import org.hamcrest.Matcher
import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class LibraryFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: LibraryRepository = mock(LibraryRepository::class.java)

    private val navController = mock(NavController::class.java)

    private val testProfile = UserProfile(
        username = "TestUser",
        bio = "Hello World",
        profileUrl = null,
        reviewCount = 5,
        followerCount = 10,
        followingCount = 10,
        favoriteGenres = listOf("SF", "Mystery"),
        preferences = UserPreferences(
            tradeLocation1 = null,
            tradeLocation2 = null,
            tradeSpot1 = "Gangnam Station",
            tradeSpot2 = null,
            favBook = "Dune",
            favBookNote = "Best Sci-Fi",
            favAuthor = "Frank Herbert",
            favAuthorNote = "Genius",
            readingHabit = "Night"
        )
    )


    @Before
    fun setup() {
        hiltRule.inject()

        runBlocking {
            `when`(mockRepo.getMyProfile()).thenReturn(testProfile)
            `when`(mockRepo.getMyReviews()).thenReturn(emptyList())
            `when`(mockRepo.getMyBooks()).thenReturn(emptyList())
            `when`(mockRepo.getMyWishlist()).thenReturn(emptyList())
        }
    }

    // Test 1: observeViewModel & syncChipsFromProfile
    @Test
    fun displayProfile_showsCorrectDataAndChips() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.tvName)).check(matches(withText("TestUser")))
        onView(withId(R.id.tvBio)).check(matches(withText("Hello World")))

//        onView(withId(R.id.chipGroupLocations))
//            .check(matches(hasDescendant(withText("Seoul Gangnam"))))
    }

    @Test
    fun switchTabs_updatesFabIcon() {
        launchLibraryFragment()

        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_add_review)))

        onView(withText(R.string.shelf)).perform(click())
        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_add_book)))

        onView(withText(R.string.profile)).perform(click())
        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_edit_profile)))
    }

    @Test
    fun clickEditProfile_togglesUiVisibility() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.tvTradeSpot1)).check(matches(isDisplayed()))
        onView(withId(R.id.editTradeSpot1)).check(matches(not(isDisplayed())))

        onView(withId(R.id.fabAdd)).perform(click())

        onView(withId(R.id.tvTradeSpot1)).check(matches(not(isDisplayed())))
        onView(withId(R.id.editTradeSpot1)).check(matches(isDisplayed()))

        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_save_profile)))
    }

    @Test
    fun addLocation_addsNewChip() {
        launchLibraryFragment()
        onView(withText(R.string.profile)).perform(click())
        onView(withId(R.id.fabAdd)).perform(click()) // 편집 모드 진입

        onView(withId(R.id.autoCompleteLocation1))
            .perform(scrollTo(), replaceText("Busan"), closeSoftKeyboard())

        onView(withId(R.id.autoCompleteLocation2))
            .perform(scrollTo(), replaceText("Haeundae"), closeSoftKeyboard())

        onView(withId(R.id.btnAddLocation)).perform(forceClick())

        onView(withId(R.id.chipGroupLocations))
//            .perform(scrollTo())
            .check(matches(hasDescendant(withText("Busan Haeundae"))))

        onView(withId(R.id.autoCompleteLocation1)).check(matches(withText("")))
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

    private fun forceClick(): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return isDisplayed()
            }

            override fun getDescription(): String {
                return "force click"
            }

            override fun perform(uiController: UiController, view: View) {
                view.performClick()
            }
        }
    }
}
