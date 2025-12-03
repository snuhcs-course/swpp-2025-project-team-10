package com.example.librarytogether.feature.library

import android.os.Looper
import android.view.View
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.closeSoftKeyboard
import androidx.test.espresso.action.ViewActions.replaceText
import androidx.test.espresso.action.ViewActions.scrollTo
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withContentDescription
import androidx.test.espresso.matcher.ViewMatchers.withEffectiveVisibility
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.Matcher
import org.hamcrest.Matchers.not
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
            favBooks = listOf("Dune"),
            favBookNotes = listOf("Best Sci-Fi"),
            favAuthors = listOf("Frank Herbert"),
            favAuthorNotes = listOf("Genius"),
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
        onView(withId(R.id.tvBio)).check(matches(withText("Night")))
    }

    @Test
    fun switchTabs_updatesFabIcon() {
        launchLibraryFragment()

        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_add_review)))

        onView(withText(R.string.shelf)).perform(click())

        onView(withId(R.id.tvBookEmpty)).check(matches(isDisplayed()))

        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_add_book)))

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.profileContainer)).check(matches(isDisplayed()))

        onView(withId(R.id.fabAdd))
            .check(matches(withContentDescription(R.string.fab_edit_profile)))
    }

    @Test
    fun clickEditProfile_togglesUiVisibility() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.tvTradeSpot1))
            .check(matches(withEffectiveVisibility(ViewMatchers.Visibility.VISIBLE)))
        onView(withId(R.id.editTradeSpot1))
            .check(matches(withEffectiveVisibility(ViewMatchers.Visibility.GONE)))

        onView(withId(R.id.fabAdd)).perform(click())

        onView(withId(R.id.tvTradeSpot1))
            .check(matches(withEffectiveVisibility(ViewMatchers.Visibility.GONE)))
        onView(withId(R.id.editTradeSpot1))
            .check(matches(withEffectiveVisibility(ViewMatchers.Visibility.VISIBLE)))

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

        // 텍스트 입력 후 UI 상태 반영 대기
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        onView(withId(R.id.btnAddLocation)).perform(forceClick())

        onView(withId(R.id.chipGroupLocations))
            .check(matches(hasDescendant(withText("Busan Haeundae"))))

        onView(withId(R.id.autoCompleteLocation1)).check(matches(withText("")))
    }

    @Test
    fun fab_onReviewsTab_navigatesToWriteReview() {
        launchLibraryFragment()

        onView(withId(R.id.fabAdd)).perform(click())

        verify(navController).navigate(R.id.action_libraryFragment_to_writeReviewFragment)
    }

    @Test
    fun fab_onShelfTab_navigatesToAddBook() {
        launchLibraryFragment()

        onView(withText(R.string.shelf)).perform(click())
        onView(withId(R.id.fabAdd)).perform(click())

        verify(navController).navigate(
            LibraryFragmentDirections.actionLibraryFragmentToAddBookFragment()
        )
    }

    @Test
    fun saveProfileFromEditMode_exitsEditModeAndKeepsViewVisible() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.fabAdd)).perform(click())

        onView(withId(R.id.editFavBook))
            .perform(scrollTo(), replaceText("New Fav Book"), closeSoftKeyboard())

        onView(withId(R.id.fabAdd)).perform(click())

        onView(withId(R.id.editFavBook)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvFavBook)).check(matches(isDisplayed()))
    }

    @Test
    fun profileGenres_renderedAsChips() {
        launchLibraryFragment()

        onView(withText(R.string.profile)).perform(click())

        onView(withId(R.id.groupSelectedGenres))
            .check(matches(hasDescendant(withText("SF"))))
        onView(withId(R.id.groupSelectedGenres))
            .check(matches(hasDescendant(withText("Mystery"))))

        onView(withId(R.id.tvGenreNone)).check(matches(not(isDisplayed())))
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
