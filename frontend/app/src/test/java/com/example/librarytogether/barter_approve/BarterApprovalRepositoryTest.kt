package com.example.librarytogether.feature.barterapproval

import android.util.Log
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalApi
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalRepository
import com.example.librarytogether.feature.library.data.Book
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
class BarterApprovalRepositoryTest {

    private lateinit var api: BarterApprovalApi
    private lateinit var repo: BarterApprovalRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = BarterApprovalRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    private fun createDetail(id: String = "req-1") = BarterApprovalDetail(
        id = id,
        requesterName = "User",
        requesterAvatarUrl = null,
        createdAt = "2025-01-01",
        books = emptyList(),
        message = listOf("Msg")
    )

    // --- getBarterApproval ---

    @Test
    fun getBarterApproval_success_returns_detail() = runTest {
        val detail = createDetail("req-1")
        whenever(api.getBarterApproval("req-1")).thenReturn(Response.success(detail))

        val result = repo.getBarterApproval("req-1")

        assertThat(result, equalTo(detail))
    }

    @Test
    fun getBarterApproval_failure_throws_exception_and_logs() = runTest {
        val errorBody = "{}".toResponseBody("application/json".toMediaTypeOrNull())
        whenever(api.getBarterApproval("req-1")).thenReturn(Response.error(404, errorBody))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getBarterApproval("req-1")
            }
        }
        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    @Test
    fun getBarterApproval_exception_rethrows() = runTest {
        whenever(api.getBarterApproval("req-1")).thenThrow(RuntimeException("Network"))

        assertThrows(RuntimeException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.getBarterApproval("req-1")
            }
        }
    }

    // --- acceptBook ---

    @Test
    fun acceptBook_success_completes() = runTest {
        whenever(api.acceptBook("req-1", "book-1")).thenReturn(Response.success(Unit))

        repo.acceptBook("req-1", "book-1")

        verify(api).acceptBook("req-1", "book-1")
    }

    @Test
    fun acceptBook_failure_throws_exception() = runTest {
        val errorBody = "".toResponseBody(null)
        whenever(api.acceptBook("req-1", "book-1")).thenReturn(Response.error(500, errorBody))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.acceptBook("req-1", "book-1")
            }
        }
    }

    // --- rejectRequest ---

    @Test
    fun rejectRequest_success_completes() = runTest {
        whenever(api.rejectRequest("req-1")).thenReturn(Response.success(Unit))

        repo.rejectRequest("req-1")

        verify(api).rejectRequest("req-1")
    }

    @Test
    fun rejectRequest_failure_throws_exception() = runTest {
        val errorBody = "".toResponseBody(null)
        whenever(api.rejectRequest("req-1")).thenReturn(Response.error(400, errorBody))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repo.rejectRequest("req-1")
            }
        }
    }
}
