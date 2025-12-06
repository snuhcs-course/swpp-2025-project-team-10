package com.example.librarytogether.feature.barterapproval

import android.os.Bundle
import android.view.View
import androidx.appcompat.widget.AppCompatImageButton
import androidx.lifecycle.MutableLiveData
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.barterapproval.BarterApprovalViewModel.UiState
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.not
import org.hamcrest.Matcher
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.Mockito.doAnswer
import org.mockito.Mockito.doReturn
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class BarterApprovalFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockViewModel: BarterApprovalViewModel = mock(BarterApprovalViewModel::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    private val stateLiveData = MutableLiveData<UiState>()
    private val testRequestId = "req-123"

    private val mockBook = Book(
        id = "book-1",
        title = "테스트 책",
        authors = listOf("테스트 작가"),
        cover_image = "http://example.com/cover.png",
        publisher = "테스트 출판사",
        isbn = "9781234567890",
        publicationId = "pub-1"
    )

    private val mockDetail = BarterApprovalDetail(
        requesterName = "홍길동",
        requesterAvatarUrl = "http://example.com/avatar.png",
        createdAt = "2025-11-13 17:00",
        message = listOf("이 책 갖고 싶어요", "제 책이랑 바꿔요"),
        books = listOf(mockBook),
        id = "i"
    )

    @Before
    fun setup() {
        hiltRule.inject()
        doReturn(stateLiveData).`when`(mockViewModel).state
    }

    @Test
    fun renderLoading_showsProgressBar_and_hidesContent() {
        // Given
        stateLiveData.postValue(UiState.Loading)

        // When
        launchBarterApprovalFragment()

        // Then
        onView(withId(R.id.progress)).check(matches(isDisplayed()))
        onView(withId(R.id.contentGroup)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvError)).check(matches(not(isDisplayed())))
    }

    @Test
    fun renderError_showsErrorMessage() {
        // Given
        val errorMsg = "네트워크 오류 발생"
        stateLiveData.postValue(UiState.Error(errorMsg))

        // When
        launchBarterApprovalFragment()

        // Then
        onView(withId(R.id.tvError)).check(matches(isDisplayed()))
        onView(withId(R.id.tvError)).check(matches(withText(errorMsg)))
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
    }

    @Test
    fun renderData_displaysDetailInfoAndList() {
        // Given
        stateLiveData.postValue(UiState.Data(mockDetail))

        // When
        launchBarterApprovalFragment()

        // Then
        onView(withId(R.id.tvRequesterName)).check(matches(withText("홍길동")))
//        onView(withId(R.id.tvCreatedAt)).check(matches(withText("2025-11-13 17:00")))
        onView(withId(R.id.rvBooks)).check(matches(isDisplayed()))
        onView(withText("테스트 책")).check(matches(isDisplayed()))
        onView(withText("테스트 작가")).check(matches(isDisplayed()))
    }

    @Test
    fun clickToolbarNavigation_popsBackStack() {
        // Given
        stateLiveData.postValue(UiState.Data(mockDetail))
        launchBarterApprovalFragment()

        // When
        onView(
            allOf(
                withParent(withId(R.id.toolbar)),
                isAssignableFrom(AppCompatImageButton::class.java)
            )
        ).perform(click())

        // Then
        verify(mockNavController).popBackStack()
    }

    @Test
    fun clickRejectButton_callsViewModelReject_andPopsStack() {
        // Given
        stateLiveData.postValue(UiState.Data(mockDetail))
        launchBarterApprovalFragment()

        doAnswer { invocation ->
            val callback = invocation.arguments[0] as () -> Unit
            callback.invoke()
            null
        }.`when`(mockViewModel).rejectRequest(ArgumentMatchers.any() ?: {})

        // When
        onView(withId(R.id.btnReject)).perform(click())

        // Then
        verify(mockViewModel).rejectRequest(ArgumentMatchers.any() ?: {})
        verify(mockNavController).popBackStack()
    }

    @Test
    fun clickBookItem_navigatesToBookDetail() {
        // Given
        stateLiveData.postValue(UiState.Data(mockDetail))
        launchBarterApprovalFragment()

        // When
        onView(withId(R.id.rvBooks))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    click()
                )
            )

        // Then
        val expectedDirection = BarterApprovalFragmentDirections
            .actionBarterApprovalFragmentToBookDetailFragment(
                bookId = mockBook.id,
                source = EntrySource.BARTERAPPROVAL,
                barterMessage = "이 책 갖고 싶어요",
                barterRequestId = testRequestId
            )

        verify(mockNavController).navigate(expectedDirection)
    }

    @Test
    fun clickBookAcceptAction_callsViewModelAccept() {
        // Given
        stateLiveData.postValue(UiState.Data(mockDetail))
        launchBarterApprovalFragment()

        // When
        onView(withId(R.id.rvBooks))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(R.id.btnAction)
                )
            )

        // Then
        verify(mockViewModel).acceptBook(mockBook)
    }

    private fun launchBarterApprovalFragment() {
        val args = Bundle().apply {
            putString("requestId", testRequestId)
        }

        launchFragmentInHiltContainer<BarterApprovalFragment>(fragmentArgs = args) {
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
                v?.performClick()
            }
        }
    }
}
