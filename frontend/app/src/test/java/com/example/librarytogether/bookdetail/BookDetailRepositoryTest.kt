package com.example.librarytogether.feature.bookdetail

import android.util.Log
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.bookdetail.data.BookDetailApi
import com.example.librarytogether.feature.bookdetail.data.BookRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
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
class BookDetailRepositoryTest {

    private lateinit var api: BookDetailApi
    private lateinit var repo: BookRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = BookRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    private fun createBookDetail(id: String = "book-1") = BookDetail(
        id = id,
        title = "Kotlin In Action",
        authors = "JetBrains",
        publisher = "Manning",
        isbn_13 = "978-1234567890",
        description = "Great book",
        cover_image = "http://example.com/cover.jpg",
        is_for_barter = true,
        owner = "User1"
    )

    @Test
    fun getBookDetail_success_returns_detail() = runTest {
        val detail = createBookDetail("book-1")
        whenever(api.getBook("book-1")).thenReturn(Response.success(detail))

        val result = repo.getBookDetail("book-1")

        assertThat(result, equalTo(detail))
        assertThat(result.title, equalTo("Kotlin In Action"))
    }

    @Test
    fun getBookDetail_success_but_null_body_throws_exception() = runTest {
        val response: Response<BookDetail> = Response.success(null)
        whenever(api.getBook("book-1")).thenReturn(response)

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getBookDetail("book-1")
            }
        }
    }

    @Test
    fun getBookDetail_api_failure_throws_exception_and_logs() = runTest {
        val errorBody = "{}".toResponseBody("application/json".toMediaTypeOrNull())
        whenever(api.getBook("book-1")).thenReturn(Response.error(404, errorBody))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getBookDetail("book-1")
            }
        }
        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    @Test
    fun getBookDetail_network_exception_rethrows_and_logs() = runTest {
        whenever(api.getBook(any())).thenThrow(RuntimeException("Network Error"))

        assertThrows(RuntimeException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getBookDetail("book-1")
            }
        }
        mockedLog.verify { Log.e(any(), any(), any()) }
    }
}
