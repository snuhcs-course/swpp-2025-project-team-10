package com.example.librarytogether.feature.comment

import androidx.core.os.bundleOf
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.SmallTest
import com.example.librarytogether.R
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.comment.data.CommentRepository
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import com.example.librarytogether.util.CustomViewActions.clickChildViewWithId
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.junit.Before
import org.junit.Ignore
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.any
import org.mockito.Mockito.atLeastOnce
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`


@SmallTest
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class CommentBottomSheetTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: CommentRepository = mock(CommentRepository::class.java)

    private val initial = listOf(
        CommentDto("1", "User1", null, "Hello", "2025", "2025", 0, false),
        CommentDto("2", "User2", null, "World", "2025", "2025", 3, true)
    )

    @Before
    fun setup() {
        hiltRule.inject()

        runBlocking {
            `when`(mockRepo.toggleCommentLike(any(), any()))
                .thenReturn(initial[0])
        }
    }

    @Test
    fun comments_are_displayed() {
        launch()

        onView(withText("Hello")).check(matches(isDisplayed()))
        onView(withText("World")).check(matches(isDisplayed()))
    }

    @Test
    suspend fun like_button_triggers_toggleLike() {
        launch()

        onView(withId(R.id.recyclerComments))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(R.id.btnLike)
                )
            )

        verify(mockRepo, atLeastOnce()).toggleCommentLike(any(), any())
    }

    private fun launch() {
        launchFragmentInHiltContainer<CommentBottomSheet>(
            fragmentArgs = bundleOf(
                "postId" to 1,
                "comments" to ArrayList(initial)
            )
        )
    }
}
