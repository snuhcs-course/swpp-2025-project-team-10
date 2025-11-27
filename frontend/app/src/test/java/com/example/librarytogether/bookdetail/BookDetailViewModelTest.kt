package com.example.librarytogether.feature.bookdetail

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.SavedStateHandle
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
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class BookDetailViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: BookRepository
    private lateinit var savedStateHandle: SavedStateHandle

    @Before
    fun setUp() {
        repo = mock()
        savedStateHandle = SavedStateHandle(mapOf("bookId" to "target-id"))
    }

    private fun createViewModel() = BookDetailViewModel(repo, savedStateHandle)

    private fun createBookDetail() = BookDetail(
        id = "target-id",
        title = "Title",
        authors = "Author",
        publisher = null,
        isbn_13 = null,
        description = "Desc",
        cover_image = null,
        is_for_barter = false,
        owner = "Owner"
    )

    @Test
    fun load_success_updates_state_to_Data() = runTest {
        val detail = createBookDetail()
        whenever(repo.getBookDetail("target-id")).thenReturn(detail)

        val vm = createViewModel()

        vm.load()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Data::class.java))
        assertThat((state as BookDetailViewModel.UiState.Data).book, equalTo(detail))

        verify(repo).getBookDetail("target-id")
    }

    @Test
    fun load_failure_updates_state_to_Error() = runTest {
        whenever(repo.getBookDetail("target-id")).thenThrow(RuntimeException("Fetch Failed"))

        val vm = createViewModel()

        vm.load()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Error::class.java))
        assertThat((state as BookDetailViewModel.UiState.Error).message, equalTo("Fetch Failed"))
    }

    @Test
    fun initialState_is_Loading() {
        val vm = createViewModel()
        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(BookDetailViewModel.UiState.Loading::class.java))
    }
}
