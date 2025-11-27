package com.example.librarytogether.feature.explore

import com.example.librarytogether.feature.explore.data.ExploreApi
import com.example.librarytogether.feature.explore.data.ExploreRepository
import com.example.librarytogether.feature.library.data.Book
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.junit.Assert.assertThrows
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class ExploreRepositoryTest {

    private lateinit var api: ExploreApi
    private lateinit var repo: ExploreRepository

    @Before
    fun setUp() {
        api = mock()
        repo = ExploreRepository(api)
    }

    private fun createBook(id: String = "1") = Book(
        id = id, title = "T", authors = "A", cover_image = null, publisher = null, isbn = null
    )

    @Test
    fun getRecommendations_success_returns_list() = runTest {
        val books = listOf(createBook("1"), createBook("2"))
        whenever(api.getRecommendations()).thenReturn(Response.success(books))

        val result = repo.getRecommendations()

        assertThat(result, hasSize(2))
        assertThat(result[0].id, equalTo("1"))
    }

    @Test
    fun getRecommendations_success_null_body_returns_empty() = runTest {
        val response: Response<List<Book>> = Response.success(null)
        whenever(api.getRecommendations()).thenReturn(response)

        val result = repo.getRecommendations()

        assertThat(result, empty())
    }

    @Test
    fun getRecommendations_failure_throws_exception() = runTest {
        whenever(api.getRecommendations()).thenReturn(Response.error(500, "".toResponseBody(null)))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getRecommendations()
            }
        }
    }

    @Test
    fun getRecommendations_network_exception_rethrows() = runTest {
        whenever(api.getRecommendations()).thenThrow(RuntimeException("Net Error"))

        assertThrows(RuntimeException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getRecommendations()
            }
        }
    }
}
