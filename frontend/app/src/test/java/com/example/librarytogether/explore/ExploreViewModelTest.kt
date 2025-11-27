package com.example.librarytogether.feature.explore

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.explore.data.ExploreRepository
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
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class ExploreViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: ExploreRepository
    private lateinit var vm: ExploreViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = ExploreViewModel(repo)
    }

    private fun createBook(id: String = "1") = Book(
        id = id, title = "T", authors = "A", cover_image = null, publisher = null, isbn = null
    )

    @Test
    fun loadRecommendations_success_sets_Data_state() = runTest {
        val books = listOf(createBook("1"))
        whenever(repo.getRecommendations()).thenReturn(books)

        vm.loadRecommendations()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(ExploreUi.Data::class.java))
        assertThat((state as ExploreUi.Data).items, hasSize(1))
        assertThat(state.items[0].id, equalTo("1"))

        verify(repo).getRecommendations()
    }

    @Test
    fun loadRecommendations_empty_sets_Empty_state() = runTest {
        whenever(repo.getRecommendations()).thenReturn(emptyList())

        vm.loadRecommendations()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(ExploreUi.Empty::class.java))
    }

    @Test
    fun loadRecommendations_failure_sets_Error_state() = runTest {
        whenever(repo.getRecommendations()).thenThrow(RuntimeException("Fetch Fail"))

        vm.loadRecommendations()
        advanceUntilIdle()

        val state = vm.state.getOrAwaitValue()
        assertThat(state, instanceOf(ExploreUi.Error::class.java))
        assertThat((state as ExploreUi.Error).message, equalTo("Fetch Fail"))
    }

    @Test
    fun initialState_is_Loading() {
        val state = vm.state.getOrAwaitValue()

        assertThat(state, instanceOf(ExploreUi.Loading::class.java))
    }
}
