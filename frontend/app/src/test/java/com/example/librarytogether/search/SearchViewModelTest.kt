package com.example.librarytogether.feature.search.data

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.search.SearchViewModel
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.containsString
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.nullValue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: SearchRepository
    private lateinit var vm: SearchViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = SearchViewModel(repo)
    }

    private fun createSearchItem(
        id: String = "book-1",
        title: String = "Kotlin In Action",
        authors: List<Int> = listOf(101)
    ): SearchItem {
        return SearchItem(
            id = id,
            title = title,
            authors = authors,
            publisher = 1,
            isbn13 = "978-1234567890",
            cover_image = null,
            is_for_barter = true
        )
    }

    @Test
    fun search_success_sets_results_and_loading_false() = runTest {
        // Arrange
        val query = "Kotlin"
        val resultList = listOf(createSearchItem())
        whenever(repo.search(query)).thenReturn(resultList)

        // Act
        vm.search(query)
        advanceUntilIdle()

        // Assert
        val results = vm.results.getOrAwaitValue()
        assertThat(results, hasSize(1))
        assertThat(results[0].title, equalTo("Kotlin In Action"))

        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.error.value, nullValue())
    }

    @Test
    fun search_exception_sets_error_and_loading_false() = runTest {
        // Arrange
        whenever(repo.search("error")).thenThrow(RuntimeException("Network Error"))

        // Act
        vm.search("error")
        advanceUntilIdle()

        // Assert
        assertThat(vm.results.getOrAwaitValue(), empty()) // 실패 시 빈 리스트 유지
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        assertThat(vm.error.getOrAwaitValue(), containsString("오류"))
    }

    @Test
    fun clearSearch_empties_results() = runTest {
        // Arrange: 검색 결과 채우기
        val resultList = listOf(createSearchItem())
        whenever(repo.search("a")).thenReturn(resultList)
        vm.search("a")
        advanceUntilIdle()
        assertThat(vm.results.getOrAwaitValue(), hasSize(1))

        // Act
        vm.clearSearch()

        // Assert
        assertThat(vm.results.getOrAwaitValue(), empty())
    }

    @Test
    fun onErrorShown_clears_error_message() = runTest {
        whenever(repo.search("fail")).thenThrow(RuntimeException("Fail"))
        vm.search("fail")
        advanceUntilIdle()
        assertThat(vm.error.getOrAwaitValue(), containsString("오류"))

        // Act
        vm.onErrorShown()

        // Assert
        assertThat(vm.error.value, nullValue())
    }
}
