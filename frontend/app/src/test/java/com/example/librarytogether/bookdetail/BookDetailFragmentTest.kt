package com.example.librarytogether.feature.bookdetail

import android.view.View
import android.widget.ImageButton
import androidx.core.os.bundleOf
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.RootMatchers.isDialog
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.bookdetail.data.BookRepository
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.not
import org.hamcrest.Matcher
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.*
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLooper
import java.util.concurrent.TimeUnit

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class BookDetailFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockBookRepo: BookRepository = mock(BookRepository::class.java)

    @BindValue
    @JvmField
    val mockHomeRepo: HomeRepository = mock(HomeRepository::class.java)

    @BindValue
    @JvmField
    val mockLibraryRepo: LibraryRepository = mock(LibraryRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    // Test Data
    private val testBookId = "book-123"
    private val testOwnerId = 99
    private val mockBookDetail = BookDetail(
        id = testBookId,
        title = "테스트 책 제목",
        authors = listOf("작가1", "작가2"),
        publisher_name = "테스트 출판사",
        isbn = "978-1234567890",
        description = "테스트 설명입니다.",
        cover_image = "https://example.com/cover.jpg",
        ownerId = testOwnerId,
        is_for_barter = true,
        owner = "OwnerName"
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    // --- 1. UI Rendering Tests ---

    @Test
    fun loadData_success_displaysBookInfo() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // Then
        onView(withId(R.id.tvTitle)).check(matches(withText("테스트 책 제목")))
        onView(withId(R.id.tvAuthor)).check(matches(withText("작가1, 작가2")))
        onView(withId(R.id.tvPublisher)).check(matches(withText("테스트 출판사")))
        onView(withId(R.id.tvIsbn)).check(matches(withText("978-1234567890")))
        onView(withId(R.id.tvDescription)).check(matches(withText("테스트 설명입니다.")))
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvError)).check(matches(not(isDisplayed())))
    }

    @Test
    fun loadData_error_displaysErrorMessage() {
        // Given
        val errorMsg = "Network Error"
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenThrow(RuntimeException(errorMsg))
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // Then
        onView(withId(R.id.tvError)).check(matches(isDisplayed()))
        onView(withId(R.id.tvError)).check(matches(withText(errorMsg)))
        onView(withId(R.id.progress)).check(matches(not(isDisplayed())))
        onView(withId(R.id.btnPrimary)).check(matches(not(isEnabled())))
    }

    // --- 2. EntrySource & Button Logic Tests ---

    @Test
    fun sourceSearch_barterAvailable_buttonEnabled() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail.copy(is_for_barter = true))
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // Then
        onView(withId(R.id.btnPrimary)).check(matches(isEnabled()))
        onView(withId(R.id.btnPrimary)).check(matches(withText(R.string.action_request_barter)))
    }

    @Test
    fun sourceSearch_barterUnavailable_buttonDisabled() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail.copy(is_for_barter = false))
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // Then
        onView(withId(R.id.btnPrimary)).check(matches(not(isEnabled())))
        onView(withId(R.id.btnPrimary)).check(matches(withText(R.string.unavailable_for_barter)))
    }

    @Test
    fun sourceMyBookshelf_buttonDisabled_unavailableText() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.MYBOOKSHELF)

        // Then
        onView(withId(R.id.btnPrimary)).check(matches(not(isEnabled())))
        onView(withId(R.id.btnPrimary)).check(matches(withText(R.string.unavailable_for_barter)))
    }

    @Test
    fun sourceBarterApproval_buttonEnabled_approveText() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.BARTERAPPROVAL)

        // Then
        onView(withId(R.id.btnPrimary)).check(matches(isEnabled()))
        onView(withId(R.id.btnPrimary)).check(matches(withText(R.string.action_barter_approve)))
    }

    // --- 3. Interaction Tests ---
    @Test
    fun clickRequestBarter_callsHomeRepository() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
            `when`(mockHomeRepo.createRequest(anyInt(), anyString())).thenReturn(true)
        }
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // When 1
        onView(withId(R.id.btnPrimary)).perform(click())

        // When 2
        onView(withText(R.string.barter_apply))
            .inRoot(isDialog())
            .perform(click())

        // Then
        runBlocking {
            verify(mockHomeRepo).createRequest(testOwnerId, testBookId)
        }
    }
    @Test
    fun clickBarterApprove_navigatesBack() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }
        launchBookDetailFragment(testBookId, EntrySource.BARTERAPPROVAL)

        // When
        onView(withId(R.id.btnPrimary)).perform(click())

        // Then
        verify(mockNavController).popBackStack(R.id.nav_notification, false)
    }

    @Test
    fun clickWishlist_togglesWishlistStatus() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList()) // Initially empty
            `when`(mockLibraryRepo.addToWishlistById(anyString())).thenReturn(true)
        }
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // When
        onView(withId(R.id.fabWishlist)).perform(click())

        // Then
        runBlocking {
            // Raw value verification to prevent NPE
            verify(mockLibraryRepo).addToWishlistById(testBookId)
        }
    }

    @Test
    fun wishlistStatus_updatesFabIcon() {
        // Given
        val wishlistedBook = Book(
            id = testBookId, title = "Title", authors = null,
            cover_image = null, publisher = null, isbn = null, publicationId = null
        )

        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(listOf(wishlistedBook))
        }

        // When
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // Then
        onView(withId(R.id.fabWishlist))
            .check(matches(withContentDescription(R.string.status_wishlist)))
    }

    @Test
    fun clickBackArrow_popsBackStack() {
        // Given
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
        }
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // When
        onView(withToolbarNavigationIcon()).perform(click())

        // Then
        verify(mockNavController).popBackStack()
    }

    @Test
    fun homeViewModel_barterError_showsSnackbar() {
        // Given
        val errorMessage = "교환 신청에 실패했어요."
        runBlocking {
            `when`(mockBookRepo.getBookDetail(testBookId)).thenReturn(mockBookDetail)
            `when`(mockLibraryRepo.getMyWishlist()).thenReturn(emptyList())
            `when`(mockHomeRepo.createRequest(anyInt(), anyString()))
                .thenThrow(IllegalStateException(errorMessage))
        }
        launchBookDetailFragment(testBookId, EntrySource.SEARCH)

        // When 1
        onView(withId(R.id.btnPrimary)).perform(click())

        // When 2
        onView(withText(R.string.barter_apply))
            .inRoot(isDialog())
            .perform(click())

        ShadowLooper.idleMainLooper(300, TimeUnit.MILLISECONDS)

        // Then
        onView(withText(errorMessage)).check(matches(isDisplayed()))
    }

    // --- Helpers ---

    private fun launchBookDetailFragment(bookId: String, source: EntrySource) {
        val bundle = bundleOf(
            "bookId" to bookId,
            "source" to source
        )
        launchFragmentInHiltContainer<BookDetailFragment>(fragmentArgs = bundle) {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                try {
                    Navigation.setViewNavController(requireView(), mockNavController)
                } catch (e: Exception) {
                }
            }
        }
    }

    private fun withToolbarNavigationIcon(): Matcher<View> {
        return allOf(
            withParent(withId(R.id.toolbar)),
            isAssignableFrom(ImageButton::class.java)
        )
    }
}
