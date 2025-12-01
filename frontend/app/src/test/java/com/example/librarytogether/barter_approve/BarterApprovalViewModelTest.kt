package com.example.librarytogether.feature.barterapproval

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.SavedStateHandle
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalRepository
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.instanceOf
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class BarterApprovalViewModelTest {

    @get:Rule
    val instantRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: BarterApprovalRepository
    private lateinit var savedStateHandle: SavedStateHandle

    @Before
    fun setUp() {
        repo = mock()
        savedStateHandle = SavedStateHandle(mapOf("requestId" to "req-123"))
    }

    private fun createViewModel() = BarterApprovalViewModel(repo, savedStateHandle)

    private fun createBook(id: String) = Book(
        id = id, title = "T", authors = "A", cover_image = null, publisher = null, isbn = null
    )

    private fun createDetail(books: List<Book> = emptyList()) = BarterApprovalDetail(
        id = "req-123",
        requesterName = "User",
        requesterAvatarUrl = null,
        createdAt = "2025-01-01",
        books = books,
        message = emptyList()
    )

    // --- Load (init block) ---

    @Test
    fun load_success_sets_UiState_Data() = runTest {
        val detail = createDetail()
        whenever(repo.getBarterApproval("req-123")).thenReturn(detail)

        val vm = createViewModel()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BarterApprovalViewModel.UiState.Data::class.java))
        assertThat((state as BarterApprovalViewModel.UiState.Data).detail, equalTo(detail))
    }

    @Test
    fun load_failure_sets_UiState_Error() = runTest {
        whenever(repo.getBarterApproval("req-123")).thenThrow(RuntimeException("Fail"))

        val vm = createViewModel()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BarterApprovalViewModel.UiState.Error::class.java))
        assertThat((state as BarterApprovalViewModel.UiState.Error).message, equalTo("Fail"))
    }

    // --- Accept Book ---

    @Test
    fun acceptBook_success_removes_book_from_list() = runTest {
        // Arrange
        val book1 = createBook("b1")
        val book2 = createBook("b2")
        val initialDetail = createDetail(listOf(book1, book2))
        whenever(repo.getBarterApproval("req-123")).thenReturn(initialDetail)
        whenever(repo.acceptBook("req-123", "b1")).thenReturn(Unit)

        val vm = createViewModel()
        advanceUntilIdle() // Load 완료

        // Act
        vm.acceptBook(book1)
        advanceUntilIdle()

        // Assert
        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BarterApprovalViewModel.UiState.Data::class.java))

        val currentBooks = (state as BarterApprovalViewModel.UiState.Data).detail.books
        assertThat(currentBooks, hasSize(1))
        assertThat(currentBooks[0].id, equalTo("b2")) // b1은 제거됨

        verify(repo).acceptBook("req-123", "b1")
    }

    @Test
    fun acceptBook_failure_sets_UiState_Error() = runTest {
        // Arrange
        val book1 = createBook("b1")
        val detail = createDetail(listOf(book1))
        whenever(repo.getBarterApproval("req-123")).thenReturn(detail)
        whenever(repo.acceptBook("req-123", "b1")).thenThrow(RuntimeException("Accept Fail"))

        val vm = createViewModel()
        advanceUntilIdle()

        // Act
        vm.acceptBook(book1)
        advanceUntilIdle()

        // Assert
        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BarterApprovalViewModel.UiState.Error::class.java))
        assertThat((state as BarterApprovalViewModel.UiState.Error).message, equalTo("Accept Fail"))
    }

    // --- Reject Request ---

    @Test
    fun rejectRequest_success_invokes_callback() = runTest {
        whenever(repo.getBarterApproval("req-123")).thenReturn(createDetail())
        whenever(repo.rejectRequest("req-123")).thenReturn(Unit)

        val vm = createViewModel()
        advanceUntilIdle()

        var callbackInvoked = false
        vm.rejectRequest { callbackInvoked = true }
        advanceUntilIdle()

        assertThat(callbackInvoked, equalTo(true))
        verify(repo).rejectRequest("req-123")
    }

    @Test
    fun rejectRequest_failure_sets_UiState_Error() = runTest {
        whenever(repo.getBarterApproval("req-123")).thenReturn(createDetail())
        whenever(repo.rejectRequest("req-123")).thenThrow(RuntimeException("Reject Fail"))

        val vm = createViewModel()
        advanceUntilIdle()

        vm.rejectRequest { }
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BarterApprovalViewModel.UiState.Error::class.java))
        assertThat((state as BarterApprovalViewModel.UiState.Error).message, equalTo("Reject Fail"))
    }

    // --- Toggle Selected Book ---

    @Test
    fun toggleSelectedBook_selects_and_deselects() = runTest {
        // Arrange
        whenever(repo.getBarterApproval(any())).thenReturn(createDetail())
        val vm = createViewModel()
        val book = createBook("b1")

        // Act 1: Select
        vm.toggleSelectedBook(book)
        assertThat(vm.selectedBook.getOrAwaitValue(), equalTo(book))

        // Act 2: Deselect (Toggle same book)
        vm.toggleSelectedBook(book)
        assertThat(vm.selectedBook.getOrAwaitValue(), equalTo(null))

        // Act 3: Select another (Switch)
        val book2 = createBook("b2")
        vm.toggleSelectedBook(book)
        vm.toggleSelectedBook(book2)
        assertThat(vm.selectedBook.getOrAwaitValue(), equalTo(book2))
    }
}
