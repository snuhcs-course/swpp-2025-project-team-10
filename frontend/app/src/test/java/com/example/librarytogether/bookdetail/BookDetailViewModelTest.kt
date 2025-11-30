package com.example.librarytogether.feature.bookdetail

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.SavedStateHandle
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalRepository
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.bookdetail.data.BookRepository
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class BookDetailViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var bookRepository: BookRepository
    private lateinit var barterApprovalRepository: BarterApprovalRepository
    private lateinit var savedStateHandle: SavedStateHandle

    @Before
    fun setUp() {
        savedStateHandle = SavedStateHandle(mapOf("bookId" to "target-id"))
        bookRepository = mock()
        barterApprovalRepository = mock()
    }

    private fun createViewModel() =
        BookDetailViewModel(bookRepository, barterApprovalRepository, savedStateHandle)

    private fun createBookDetail() = BookDetail(
        id = "target-id",
        title = "Title",
        authors = listOf("Author"),
        publisher = null,
        isbn = null,
        description = "Desc",
        cover_image = null,
        is_for_barter = false,
        owner = "Owner"
    )

    @Test
    fun load_success_updates_state_to_Data() = runTest {
        val detail = createBookDetail()
        whenever(bookRepository.getBookDetail("target-id")).thenReturn(detail)

        val vm = createViewModel()

        vm.load()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Data::class.java))
        assertThat((state as BookDetailViewModel.UiState.Data).book, equalTo(detail))

        verify(bookRepository).getBookDetail("target-id")
    }

    @Test
    fun load_failure_updates_state_to_Error() = runTest {
        whenever(bookRepository.getBookDetail("target-id"))
            .thenThrow(RuntimeException("Fetch Failed"))

        val vm = createViewModel()

        vm.load()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Error::class.java))
        assertThat((state as BookDetailViewModel.UiState.Error).message, equalTo("Fetch Failed"))
    }

    @Test
    fun load_failure_withNullMessage_uses_defaultMessage() = runTest {
        whenever(bookRepository.getBookDetail("target-id"))
            .thenThrow(RuntimeException())

        val vm = createViewModel()

        vm.load()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Error::class.java))
        assertThat((state as BookDetailViewModel.UiState.Error).message, equalTo("error"))
    }

    @Test
    fun initialState_is_Loading() {
        val vm = createViewModel()
        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Loading::class.java))
    }

    @Test
    fun initialAcceptState_is_Idle() {
        val vm = createViewModel()
        val acceptState = vm.acceptState.getOrAwaitValue()
        assertThat(acceptState, instanceOf(BookDetailViewModel.AcceptState.Idle::class.java))
    }

    @Test
    fun acceptSelectedBook_withoutRequestId_doesNothing_andStateRemainsIdle() = runTest {
        val vm = createViewModel()

        vm.acceptSelectedBook()
        advanceUntilIdle()

        verify(barterApprovalRepository, never()).acceptBook(any(), any())

        val acceptState = vm.acceptState.getOrAwaitValue()
        assertThat(acceptState, instanceOf(BookDetailViewModel.AcceptState.Idle::class.java))
    }

    @Test
    fun acceptSelectedBook_success_updates_acceptState_to_Success() = runTest {
        savedStateHandle = SavedStateHandle(
            mapOf(
                "bookId" to "target-id",
                "barterRequestId" to "request-id"
            )
        )
        whenever(barterApprovalRepository.acceptBook("request-id", "target-id"))
            .thenReturn(Unit)

        val vm = createViewModel()

        vm.acceptSelectedBook()
        advanceUntilIdle()

        val acceptState = vm.acceptState.getOrAwaitValue()
        assertThat(acceptState, instanceOf(BookDetailViewModel.AcceptState.Success::class.java))
        verify(barterApprovalRepository).acceptBook("request-id", "target-id")
    }

    @Test
    fun acceptSelectedBook_failure_updates_acceptState_to_Error() = runTest {
        savedStateHandle = SavedStateHandle(
            mapOf(
                "bookId" to "target-id",
                "barterRequestId" to "request-id"
            )
        )
        whenever(barterApprovalRepository.acceptBook("request-id", "target-id"))
            .thenThrow(RuntimeException("Accept Failed"))

        val vm = createViewModel()

        vm.acceptSelectedBook()
        advanceUntilIdle()

        val acceptState = vm.acceptState.getOrAwaitValue()
        assertThat(acceptState, instanceOf(BookDetailViewModel.AcceptState.Error::class.java))
        assertThat(
            (acceptState as BookDetailViewModel.AcceptState.Error).message,
            equalTo("Accept Failed")
        )
    }

    @Test
    fun acceptSelectedBook_failureWithNullMessage_usesDefaultErrorMessage() = runTest {
        savedStateHandle = SavedStateHandle(
            mapOf(
                "bookId" to "target-id",
                "barterRequestId" to "request-id"
            )
        )
        whenever(barterApprovalRepository.acceptBook("request-id", "target-id"))
            .thenThrow(RuntimeException())

        val vm = createViewModel()

        vm.acceptSelectedBook()
        advanceUntilIdle()

        val acceptState = vm.acceptState.getOrAwaitValue()
        assertThat(acceptState, instanceOf(BookDetailViewModel.AcceptState.Error::class.java))
        assertThat(
            (acceptState as BookDetailViewModel.AcceptState.Error).message,
            equalTo("알 수 없는 오류가 발생했습니다.")
        )
    }
}
