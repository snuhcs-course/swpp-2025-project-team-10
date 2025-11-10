package com.example.librarytogether.library

import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import com.example.librarytogether.R
import com.example.librarytogether.fake.FakeLibraryRepository
import com.example.librarytogether.feature.library.LibraryFragment
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.CoreMatchers.not
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import javax.inject.Inject

@HiltAndroidTest
class LibraryFragmentTest {

    @get:Rule(order = 0)
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    var fakeRepository: FakeLibraryRepository = FakeLibraryRepository()

    @Before
    fun setUp() {
        hiltRule.inject()
    }

    @Test
    fun whenReviewsExist_recyclerViewIsDisplayed_andShowsCorrectData() {
        // Given:
        val fakeReviews = listOf(LibraryFixtures.review(1), LibraryFixtures.review(2))
        (fakeRepository as FakeLibraryRepository).setReviews(fakeReviews)

        // When:
        launchFragmentInHiltContainer<LibraryFragment>()

        // Then:
        onView(withId(R.id.rvReviews)).check(matches(hasMinimumChildCount(1)))

        onView(withId(R.id.tvReviewEmpty)).check(matches(not(isDisplayed())))

        onView(withId(R.id.rvReviews))
            .perform(RecyclerViewActions.scrollTo<RecyclerView.ViewHolder>(
                hasDescendant(withText("T1"))
            ))

        onView(withText("T1")).check(matches(isDisplayed()))
    }


    @Test
    fun whenReviewsAreEmpty_emptyViewIsDisplayed_andRecyclerViewIsGone() {
        // Given:
        (fakeRepository as FakeLibraryRepository).setReviews(emptyList())

        // When:
        launchFragmentInHiltContainer<LibraryFragment>()

        // Then:
        onView(withId(R.id.tvReviewEmpty)).check(matches(isDisplayed()))

        onView(withId(R.id.rvReviews)).check(matches(withEffectiveVisibility(Visibility.GONE)))
    }

    @Test
    fun clickBookTab_showsBookContent() {
        // Given:
        (fakeRepository as FakeLibraryRepository).setBooks(listOf(LibraryFixtures.book(1)))

        // When:
        launchFragmentInHiltContainer<LibraryFragment>()
        onView(withText("책장")).perform(click())

        // Then:
        onView(withId(R.id.rvBooks)).check(matches(isDisplayed()))

        onView(withId(R.id.rvReviews)).check(matches(withEffectiveVisibility(Visibility.GONE)))
    }
}
