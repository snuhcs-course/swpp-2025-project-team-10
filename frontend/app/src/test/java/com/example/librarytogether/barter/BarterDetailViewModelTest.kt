package com.example.librarytogether.feature.barter

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.barter.data.BarterDetailResponse
import com.example.librarytogether.feature.barter.data.BarterOfferRequest
import com.example.librarytogether.feature.barter.data.BarterRepository
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.library.data.UserProfile
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue

@OptIn(ExperimentalCoroutinesApi::class)
class BarterDetailViewModelTest {

    @get:Rule val instant = InstantTaskExecutorRule()
    @get:Rule val main = MainDispatcherRule()

    private lateinit var repo: BarterRepository
    private lateinit var vm: BarterDetailViewModel

    private fun detail(bookId: Int = 1) = BarterDetailResponse(
        book = Book(bookId, "T$bookId", "A", coverUrl = null, isbn = null, publisher = null),
        owner = UserProfile(
            username = "u",
            profileUrl = "",
            bio = "",
            reviewCount = 0,
            followerCount = 0,
            followingCount = 0,
            favoriteGenres = emptyList(),
            preferences = UserPreferences(null, null, null, null, null, null, null, null, null)),
        relatedReview = null
    )

    @Before
    fun setUp() {
        repo = mock()
        vm = BarterDetailViewModel(repo)
    }

    @Test
    fun loadDetails_success_sets_detail_and_loading_false() = runTest {
        whenever(repo.getBarterDetails(10)).thenReturn(detail(10))

        vm.loadDetails(10)
        advanceUntilIdle()

        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.barterDetails.getOrAwaitValue()?.book?.id, equalTo(10))
    }

    @Test
    fun loadDetails_repo_throws_sets_error_and_loading_false() = runTest {
        // Repository는 보통 null 반환으로 예외를 숨기지만, 실제 throw 도 방어
        whenever(repo.getBarterDetails(10)).thenAnswer { throw RuntimeException("boom") }

        vm.loadDetails(10)
        advanceUntilIdle()

        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.error.getOrAwaitValue(), containsString("실패"))
    }

    @Test
    fun selectBook_sets_selectedBook() = runTest {
        val b = Book(2, "T2", "A", null, null, null)

        vm.selectBook(b)

        assertThat(vm.selectedBook.getOrAwaitValue()?.id, equalTo(2))
    }

    @Test
    fun submitOffer_without_selectedBook_sets_error() = runTest {
        // details 먼저 세팅(내 책을 아직 선택하지 않은 상태)
        whenever(repo.getBarterDetails(1)).thenReturn(detail(1))
        vm.loadDetails(1)
        advanceUntilIdle()

        vm.submitOffer("hi")

        assertThat(vm.error.getOrAwaitValue(), containsString("교환할 책을 선택"))
    }

    @Test
    fun submitOffer_success_navigates_and_can_reset_flag() = runTest {
        whenever(repo.getBarterDetails(1)).thenReturn(detail(1))
        vm.loadDetails(1)
        advanceUntilIdle()

        val myBook = Book(5, "Mine", "A", null, null, null)
        vm.selectBook(myBook)

        whenever(repo.submitOffer(any())).thenReturn(true)

        vm.submitOffer("please")
        advanceUntilIdle()

        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.navigateToOfferComplete.getOrAwaitValue(), equalTo(true))

        vm.onNavigationComplete()
        assertThat(vm.navigateToOfferComplete.getOrAwaitValue(), equalTo(false))
    }

    @Test
    fun submitOffer_failure_sets_error_and_loading_false() = runTest {
        whenever(repo.getBarterDetails(1)).thenReturn(detail(1))
        vm.loadDetails(1)
        advanceUntilIdle()

        vm.selectBook(Book(3, "Mine", "A", null, null, null))
        whenever(repo.submitOffer(any())).thenReturn(false)

        vm.submitOffer("nope")
        advanceUntilIdle()

        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.error.getOrAwaitValue(), containsString("실패"))
    }


}
