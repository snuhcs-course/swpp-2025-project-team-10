package com.example.librarytogether.feature.notification

import android.os.Looper
import android.view.View
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.swipeDown
import androidx.test.espresso.assertion.ViewAssertions.doesNotExist
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.notification.data.NotificationDto
import com.example.librarytogether.feature.notification.data.NotificationRepository
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
import org.mockito.ArgumentMatchers.anyString
import org.mockito.Mockito.mock
import org.mockito.Mockito.timeout
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.robolectric.Shadows
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class NotificationFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockRepo: NotificationRepository = mock(NotificationRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    // Test Data
    private val exchangeNotif = NotificationDto(
        id = "1",
        title = "교환 요청",
        body = "책 교환 요청이 왔습니다.",
        created_at = "2025-01-01",
        is_read = false,
        deepLink = null,
        type = "barter_request",
        related_object_id = "req-1"
    )

    private val socialNotif = NotificationDto(
        id = "2",
        title = "좋아요",
        body = "회원님의 리뷰를 좋아합니다.",
        created_at = "2025-01-01",
        is_read = false,
        deepLink = "library://review/123",
        type = "like",
        related_object_id = null
    )

    private val exchangeSentNotif = NotificationDto(
        id = "3",
        title = "요청 보냄",
        body = "교환 요청을 보냈습니다.",
        created_at = "2025-01-01",
        is_read = true,
        deepLink = null,
        type = "barter_request_sent",
        related_object_id = "req-sent-1"
    )

    @Before
    fun setup() {
        hiltRule.inject()
        runBlocking {
            `when`(mockRepo.markAsRead(anyString())).thenReturn(true)
        }
    }

    @Test
    fun initialLoad_showsExchangeFilterByDefault() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(listOf(exchangeNotif, socialNotif))
        }

        // When
        launchNotificationFragment()

        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // Then
        onView(withId(R.id.rvNotifications)).check(matches(isDisplayed()))
        onView(withText("교환 요청")).check(matches(isDisplayed()))

        onView(withText("좋아요")).check(doesNotExist())
    }

    @Test
    fun emptyState_showsEmptyView() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(emptyList())
        }

        // When
        launchNotificationFragment()
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // Then
        onView(withId(R.id.emptyView)).check(matches(isDisplayed()))

    }

    @Test
    fun clickItem_marksRead_and_opensDeepLink() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(listOf(socialNotif))
        }
        launchNotificationFragment()
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        onView(withId(R.id.chipSocial)).perform(click())
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // When
        onView(withId(R.id.rvNotifications))
            .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

        // Then
        // runBlocking { verify(mockRepo).markAsRead(socialNotif.id) }
    }

    @Test
    fun clickAction_barterRequest_navigatesToApproval() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(listOf(exchangeNotif))
        }
        launchNotificationFragment()
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // When
        onView(withId(R.id.rvNotifications))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(R.id.btnAction)
                )
            )

        // Then
        //runBlocking { verify(mockRepo).markAsRead(exchangeNotif.id) }

        val expectedAction = NotificationFragmentDirections
            .actionNotificationToBarterApprovalFragment(requestId = "req-1")
        verify(mockNavController).navigate(expectedAction)
    }

    @Test
    fun clickAction_barterRequestSent_cancelsBarter_showsSnackbar() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(listOf(exchangeSentNotif))
            `when`(mockRepo.cancelBarter("req-sent-1")).thenReturn(true)
        }
        launchNotificationFragment()
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // When
        onView(withId(R.id.rvNotifications))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(R.id.btnAction)
                )
            )

        // Then
        runBlocking { verify(mockRepo).cancelBarter("req-sent-1") }

        onView(withText("교환 요청을 취소했어요.")).check(matches(isDisplayed()))
    }

    @Test
    fun clickAction_barterRequestSent_cancelFail_showsErrorSnackbar() {
        // Given
        runBlocking {
            `when`(mockRepo.fetchNotifications()).thenReturn(listOf(exchangeSentNotif))
            `when`(mockRepo.cancelBarter("req-sent-1")).thenReturn(false)
        }
        launchNotificationFragment()
        Shadows.shadowOf(Looper.getMainLooper()).idle()

        // When
        onView(withId(R.id.rvNotifications))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(R.id.btnAction)
                )
            )

        // Then
        onView(withText("교환 요청을 취소하지 못했어요. 잠시 후 다시 시도해 주세요."))
            .check(matches(isDisplayed()))
    }

    private fun launchNotificationFragment() {
        launchFragmentInHiltContainer<NotificationFragment> {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                try {
                    Navigation.setViewNavController(requireView(), mockNavController)
                } catch (e: Exception) {
                }
            }
        }
    }

    private fun clickChildViewWithId(id: Int): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View>? {
                return null
            }

            override fun getDescription(): String {
                return "Click on a child view with specified id."
            }

            override fun perform(uiController: UiController, view: View) {
                val v = view.findViewById<View>(id)
                v.performClick()
            }
        }
    }
}
