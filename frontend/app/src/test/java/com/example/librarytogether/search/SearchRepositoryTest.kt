package com.example.librarytogether.feature.search

// 1. SearchResponse를 import 합니다.
import com.example.librarytogether.feature.search.data.SearchApi
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import com.example.librarytogether.feature.search.data.SearchResponse // <-- import 추가
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.*
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class SearchRepositoryTest {
    private lateinit var api: SearchApi
    private lateinit var repo: SearchRepository

    @Before
    fun setUp() {
        api = mock()
        repo = SearchRepository(api)
    }

    @Test
    fun search_returns_list_on_200() = runTest {
        val items = listOf(SearchItem(id = 1, bookTitle = "Kotlin", authorName = "JetBrains"))
        val responseBody = SearchResponse(results = items)
        whenever(api.search("kotlin")).thenReturn(Response.success(responseBody))

        val res = repo.search("kotlin")

        assertThat(res, hasSize(1))
        assertThat(res[0].bookTitle, equalTo("Kotlin"))
    }

    @Test
    fun search_returns_empty_on_200_but_null_body() = runTest {
        whenever(api.search("x")).thenReturn(Response.success(null))

        val res = repo.search("x")

        assertThat(res, empty())
    }

    @Test(expected = IllegalStateException::class)
    fun search_throws_on_non_200() = runTest {
        whenever(api.search("x")).thenReturn(Response.error(500, "x".toResponseBody()))

        repo.search("x")
    }

    @Test(expected = RuntimeException::class)
    fun search_rethrows_on_exception() = runTest {
        whenever(api.search(any())).thenThrow(RuntimeException("net"))

        repo.search("x")
    }
}

