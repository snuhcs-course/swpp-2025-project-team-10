package com.example.librarytogether.feature.library

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.library.LibraryViewModel
import com.example.librarytogether.feature.library.data.*
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.nullValue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.clearInvocations
import org.mockito.kotlin.mock
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@ExperimentalCoroutinesApi
class LibraryViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: LibraryRepository

    @Before
    fun setUp() {
        repo = mock()
    }

    private fun createVM(): LibraryViewModel {
        return LibraryViewModel(repo)
    }

    private suspend fun setupDefaultMocks() {
        whenever(repo.getMyReviews()).thenReturn(emptyList())
        whenever(repo.getMyBooks()).thenReturn(emptyList())
        whenever(repo.getMyProfile()).thenReturn(LibraryFixtures.profile())
        whenever(repo.getMyWishlist()).thenReturn(emptyList())
    }

    @Test
    fun init_loadsAllData_successfully() = runTest {
        val r1 = LibraryFixtures.review(1)
        val b1 = LibraryFixtures.book(1)
        val p1 = LibraryFixtures.profile()

        whenever(repo.getMyReviews()).thenReturn(listOf(r1))
        whenever(repo.getMyBooks()).thenReturn(listOf(b1))
        whenever(repo.getMyProfile()).thenReturn(p1)
        whenever(repo.getMyWishlist()).thenReturn(emptyList())
        val vm = createVM()
        advanceUntilIdle()

        assertThat(vm.myReviews.getOrAwaitValue(), hasSize(1))
        assertThat(vm.myBooks.getOrAwaitValue(), hasSize(1))
        assertThat(vm.userProfile.getOrAwaitValue()?.username, equalTo("me"))
    }

    // --- refreshMyReviews 테스트 ---

    @Test
    fun refreshMyReviews_success_updatesLiveData() = runTest {
        setupDefaultMocks()
        whenever(repo.getMyReviews()).thenReturn(listOf(LibraryFixtures.review(1)))

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.refreshMyReviews()
        advanceUntilIdle()

        // Assert
        assertThat(vm.myReviews.getOrAwaitValue(), hasSize(1))
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
    }

    @Test
    fun refreshMyReviews_exception_setsError() = runTest {
        setupDefaultMocks()
        whenever(repo.getMyReviews()).thenThrow(RuntimeException("Network Error"))

        val vm = createVM()
        advanceUntilIdle()

        vm.refreshMyReviews()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("네트워크 오류가 발생했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
    }

    // --- refreshMyBooks 테스트 ---

    @Test
    fun refreshMyBooks_exception_setsError() = runTest {
        setupDefaultMocks()
        whenever(repo.getMyBooks()).thenThrow(RuntimeException("Boom"))

        val vm = createVM()
        advanceUntilIdle()

        vm.refreshMyBooks()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("책장 목록을 불러오는 데 실패했습니다."))
    }

    // --- refreshWishlist 테스트 ---

    @Test
    fun refreshWishlist_exception_setsError() = runTest {
        setupDefaultMocks()
        whenever(repo.getMyWishlist()).thenThrow(RuntimeException("Boom"))

        val vm = createVM()
        advanceUntilIdle()

        vm.refreshWishlist()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("위시리스트를 불러오는 데 실패했습니다."))
    }

    // --- toggleWishlistById 테스트 ---

    @Test
    fun toggleWishlistById_addToWishlist_success() = runTest {
        setupDefaultMocks()
        whenever(repo.getMyWishlist()).thenReturn(emptyList()) // 비어있음 -> 추가 로직
        whenever(repo.addToWishlistById("book-1")).thenReturn(true)

        val vm = createVM()
        advanceUntilIdle()

        vm.toggleWishlistById("book-1")
        advanceUntilIdle()

        verify(repo).addToWishlistById("book-1")
        verify(repo, times(2)).getMyWishlist()
    }

    @Test
    fun toggleWishlistById_removeFromWishlist_success() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(1).copy(id = "book-1")
        whenever(repo.getMyWishlist()).thenReturn(listOf(book)) // 이미 있음 -> 삭제 로직
        whenever(repo.removeFromWishlistById("book-1")).thenReturn(true)

        val vm = createVM()
        advanceUntilIdle()

        vm.toggleWishlistById("book-1")
        advanceUntilIdle()

        verify(repo).removeFromWishlistById("book-1")
    }

    @Test
    fun toggleWishlistById_failure_setsError() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(1).copy(id = "book-1")
        whenever(repo.getMyWishlist()).thenReturn(listOf(book))
        whenever(repo.removeFromWishlistById("book-1")).thenReturn(false)

        val vm = createVM()
        advanceUntilIdle()

        vm.toggleWishlistById("book-1")
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("위시리스트에서 제거하지 못했어요."))
    }

    @Test
    fun toggleWishlistById_exception_setsError() = runTest {
        setupDefaultMocks()
        whenever(repo.addToWishlistById("new-id")).thenThrow(RuntimeException("Error"))

        val vm = createVM()
        advanceUntilIdle()

        vm.toggleWishlistById("new-id")
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("위시리스트 변경에 실패했어요."))
    }

    // --- addToWishlist (Object) 테스트 ---

    @Test
    fun addToWishlist_alreadyExists_setsError() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(1)
        whenever(repo.getMyWishlist()).thenReturn(listOf(book))

        val vm = createVM()
        advanceUntilIdle()

        vm.addToWishlist(book)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("이미 위시리스트에 있어요."))
    }

    @Test
    fun addToWishlist_success_refreshesList() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(99)
        whenever(repo.addToWishlist(book)).thenReturn(true)

        val vm = createVM()
        advanceUntilIdle()

        vm.addToWishlist(book)
        advanceUntilIdle()

        verify(repo).addToWishlist(book)
        verify(repo, times(2)).getMyWishlist()
    }

    @Test
    fun addToWishlist_failure_setsError() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(99)
        whenever(repo.addToWishlist(book)).thenReturn(false)

        val vm = createVM()
        advanceUntilIdle()

        vm.addToWishlist(book)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("위시리스트 추가에 실패했어요."))
    }

    // --- addNewBook 테스트 ---

    @Test
    fun addNewBook_success_navigates() = runTest {
        setupDefaultMocks()
        val postBook = PostBook("T", "A", null, null, true)
        whenever(repo.addBook(postBook)).thenReturn(true)

        val vm = createVM()
        advanceUntilIdle()

        clearInvocations(repo)

        vm.addNewBook(postBook)
        advanceUntilIdle()

        assertThat(vm.navigateToLibrary.getOrAwaitValue(), equalTo(true))
        verify(repo).getMyBooks() // refresh 호출 확인
    }

    @Test
    fun addNewBook_failure_setsError() = runTest {
        setupDefaultMocks()
        val postBook = PostBook("T", "A", null, null, true)
        whenever(repo.addBook(postBook)).thenReturn(false)

        val vm = createVM()
        advanceUntilIdle()

        vm.addNewBook(postBook)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("책 추가에 실패했습니다."))
    }

    @Test
    fun addNewBook_exception_setsError() = runTest {
        setupDefaultMocks()
        val postBook = PostBook("T", "A", null, null, true)
        whenever(repo.addBook(postBook)).thenThrow(RuntimeException("Api Error"))

        val vm = createVM()
        advanceUntilIdle()

        vm.addNewBook(postBook)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("책 추가 중 오류가 발생했습니다."))
    }

    // --- searchBook 테스트 ---

    @Test
    fun searchBook_success_updatesResults() = runTest {
        setupDefaultMocks()
        val results = listOf(LibraryFixtures.book(10))
        whenever(repo.searchBooks("query")).thenReturn(results)

        val vm = createVM()
        advanceUntilIdle()

        vm.searchBook("query")
        advanceUntilIdle()

        assertThat(vm.searchResults.getOrAwaitValue(), hasSize(1))
    }

    @Test
    fun searchBook_exception_setsError() = runTest {
        setupDefaultMocks()
        whenever(repo.searchBooks("query")).thenThrow(RuntimeException("Error"))

        val vm = createVM()
        advanceUntilIdle()

        vm.searchBook("query")
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("검색 중 오류가 발생했습니다."))
    }

    // --- toggleLike 테스트 ---

    @Test
    fun toggleLike_success_updatesReview() = runTest {
        setupDefaultMocks()
        val r1 = LibraryFixtures.review(1, liked = false)
        whenever(repo.getMyReviews()).thenReturn(listOf(r1))

        val vm = createVM()
        advanceUntilIdle()

        val updatedR1 = r1.copy(isLiked = true)
        whenever(repo.toggleLike(1)).thenReturn(updatedR1)

        vm.toggleLike(r1)
        advanceUntilIdle()

        val list = vm.myReviews.getOrAwaitValue()
        assertThat(list.first().isLiked, equalTo(true))
    }

    @Test
    fun toggleLike_exception_setsError() = runTest {
        setupDefaultMocks()
        val r1 = LibraryFixtures.review(1)
        whenever(repo.getMyReviews()).thenReturn(listOf(r1))

        val vm = createVM()
        advanceUntilIdle()

        whenever(repo.toggleLike(1)).thenThrow(RuntimeException("Fail"))

        vm.toggleLike(r1)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("좋아요를 토글하는 데 실패했습니다."))
    }

    // --- saveProfile 테스트 ---

    @Test
    fun saveProfile_success_updatesProfile() = runTest {
        setupDefaultMocks()
        val profile = LibraryFixtures.profile()
        whenever(repo.updateMyProfile(profile)).thenReturn(profile)

        val vm = createVM()
        advanceUntilIdle()

        vm.saveProfile(profile)
        advanceUntilIdle()

        assertThat(vm.userProfile.getOrAwaitValue()?.username, equalTo("me"))
    }

    @Test
    fun saveProfile_exception_setsError() = runTest {
        setupDefaultMocks()
        val profile = LibraryFixtures.profile()
        whenever(repo.updateMyProfile(profile)).thenThrow(RuntimeException("Fail"))

        val vm = createVM()
        advanceUntilIdle()

        vm.saveProfile(profile)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("프로필 저장에 실패했습니다."))
    }

    @Test
    fun onErrorShown_clearsError() = runTest {
        setupDefaultMocks()
        val vm = createVM()

        whenever(repo.getMyBooks()).thenThrow(RuntimeException("Boom"))
        vm.refreshMyBooks()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("책장 목록을 불러오는 데 실패했습니다."))

        vm.onErrorShown()
        assertThat(vm.error.value, nullValue())
    }

    @Test
    fun clearSearch_clearsResults() = runTest {
        setupDefaultMocks()
        val vm = createVM()

        vm.clearSearch()
        assertThat(vm.searchResults.getOrAwaitValue(), empty())
    }

    // --- isWishlisted 테스트 ---

    @Test
    fun isWishlisted_returns_true_if_book_in_wishlist() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(1).copy(id = "target-book")
        whenever(repo.getMyWishlist()).thenReturn(listOf(book))

        val vm = createVM()
        advanceUntilIdle()

        val isWishlisted = vm.isWishlisted("target-book").getOrAwaitValue()

        assertThat(isWishlisted, equalTo(true))
    }

    @Test
    fun isWishlisted_returns_false_if_book_not_in_wishlist() = runTest {
        setupDefaultMocks()
        val book = LibraryFixtures.book(1).copy(id = "other-book")
        whenever(repo.getMyWishlist()).thenReturn(listOf(book))

        val vm = createVM()
        advanceUntilIdle()

        val isWishlisted = vm.isWishlisted("target-book").getOrAwaitValue()

        assertThat(isWishlisted, equalTo(false))
    }

    // --- addNewReview 테스트 ---

    @Test
    fun addNewReview_calls_repo_and_refreshes() = runTest {
        setupDefaultMocks()
        val review = LibraryFixtures.postReview()

        whenever(repo.addReview(review)).thenReturn(Unit)

        val vm = createVM()
        advanceUntilIdle()
        clearInvocations(repo)

        vm.addNewReview(review)
        advanceUntilIdle()

        verify(repo).addReview(review)
        verify(repo).getMyReviews()
    }

    // --- onBookAddedNavigationComplete 테스트 ---

    @Test
    fun onBookAddedNavigationComplete_resets_navigation_flag() = runTest {
        setupDefaultMocks()
        val vm = createVM()

        val pb = LibraryFixtures.postBook()
        whenever(repo.addBook(pb)).thenReturn(true)
        vm.addNewBook(pb)
        advanceUntilIdle()

        assertThat(vm.navigateToLibrary.getOrAwaitValue(), equalTo(true))

        vm.onBookAddedNavigationComplete()

        assertThat(vm.navigateToLibrary.getOrAwaitValue(), equalTo(false))
    }
}
