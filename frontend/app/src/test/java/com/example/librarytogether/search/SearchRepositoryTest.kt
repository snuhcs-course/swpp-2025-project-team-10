package com.example.librarytogether.feature.search.data

import android.util.Log
import com.example.librarytogether.feature.search.data.SearchApi
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.junit.After
import org.junit.Assert.assertThrows
import org.junit.Before
import org.junit.Test
import org.mockito.MockedStatic
import org.mockito.Mockito.mockStatic
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class SearchRepositoryTest {

    private lateinit var api: SearchApi
    private lateinit var repo: SearchRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = SearchRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    private fun createSearchItem(
        id: String = "book-1",
        title: String = "Kotlin",
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
    fun search_returns_list_on_200() = runTest {
        val items = listOf(createSearchItem(title = "Kotlin In Action"))
        whenever(api.search("kotlin")).thenReturn(Response.success(items))

        val res = repo.search("kotlin")

        assertThat(res, hasSize(1))
        assertThat(res[0].title, equalTo("Kotlin In Action"))
    }

    @Test
    fun search_returns_empty_on_200_but_null_body() = runTest {
        val response: Response<List<SearchItem>> = Response.success(null)
        whenever(api.search("x")).thenReturn(response)

        val res = repo.search("x")

        assertThat(res, empty())
    }

    @Test
    fun search_throws_IllegalStateException_on_non_200() = runTest {
        val errorBody = "{}".toResponseBody("application/json".toMediaTypeOrNull())
        whenever(api.search("x")).thenReturn(Response.error(500, errorBody))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.search("x")
            }
        }

        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    @Test
    fun search_rethrows_exception_and_logs() = runTest {
        whenever(api.search(any())).thenThrow(RuntimeException("Network Error"))

        assertThrows(RuntimeException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.search("x")
            }
        }

        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    @Test
    fun searchResponse_dto_structure_test() {
        // Arrange
        val item = createSearchItem()
        val list = listOf(item)

        // Act
        val response = SearchResponse(results = list)

        // Assert
        assertThat(response.results, hasSize(1))
        assertThat(response.results[0], equalTo(item))

        // Copy method coverage
        val copy = response.copy()
        assertThat(copy, equalTo(response))
    }
}
