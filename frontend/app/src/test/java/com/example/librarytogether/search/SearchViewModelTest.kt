package com.example.librarytogether.feature.search

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {
    @get:Rule val instant = InstantTaskExecutorRule()
    @get:Rule val main = MainDispatcherRule()

    private lateinit var repo: SearchRepository
    private lateinit var vm: SearchViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = SearchViewModel(repo)
    }

    @Test
    fun search_success_sets_results_and_loading_false() = runTest {
        val searchResultList = listOf(
            SearchItem(id = 1, bookTitle = "Kotlin", authorName = "JetBrains")
        )

        whenever(repo.search("k")).thenReturn(searchResultList)

        vm.search("k")
        advanceUntilIdle()

        assertThat(vm.results.value, hasSize(1))
        assertThat(vm.isLoading.value, equalTo(false))
        assertThat(vm.error.value, nullValue())
    }

    @Test
    fun search_exception_sets_error_and_loading_false() = runTest {
        whenever(repo.search("k")).thenAnswer { throw RuntimeException("boom") }

        vm.search("k")
        advanceUntilIdle()

        assertThat(vm.results.value, empty())
        assertThat(vm.isLoading.value, equalTo(false))
        assertThat(vm.error.value, containsString("오류"))
    }

    @Test
    fun clearSearch_empties_results() = runTest {
        val searchResultList = listOf(
            SearchItem(id = 1, bookTitle = "K", authorName = "A")
        )
        whenever(repo.search("k")).thenReturn(searchResultList)

        vm.search("k")
        advanceUntilIdle()

        vm.clearSearch()

        assertThat(vm.results.value, empty())
    }

}
