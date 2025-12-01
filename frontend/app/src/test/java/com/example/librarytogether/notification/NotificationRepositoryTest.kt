package com.example.librarytogether.feature.notification

import android.util.Log
import com.example.librarytogether.feature.notification.data.NotificationApi
import com.example.librarytogether.feature.notification.data.NotificationDto
import com.example.librarytogether.feature.notification.data.NotificationRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.junit.After
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
class NotificationRepositoryTest {

    private lateinit var api: NotificationApi
    private lateinit var repo: NotificationRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = NotificationRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    private fun createNotification(id: String = "1") = NotificationDto(
        id = id,
        title = "Title",
        body = "Body",
        created_at = "2025-01-01",
        is_read = false,
        deepLink = null,
        type = null,
        related_object_id = null
    )

    // --- fetchNotifications ---

    @Test
    fun fetchNotifications_success_returns_list() = runTest {
        val list = listOf(createNotification("1"), createNotification("2"))
        whenever(api.getNotifications()).thenReturn(Response.success(list))

        val result = repo.fetchNotifications()

        assertThat(result, hasSize(2))
        assertThat(result[0].id, equalTo("1"))
    }

    @Test
    fun fetchNotifications_success_null_body_returns_empty() = runTest {
        val response: Response<List<NotificationDto>> = Response.success(null)
        whenever(api.getNotifications()).thenReturn(response)

        val result = repo.fetchNotifications()

        assertThat(result, empty())
    }

    @Test
    fun fetchNotifications_failure_returns_empty() = runTest {
        whenever(api.getNotifications()).thenReturn(Response.error(500, "".toResponseBody(null)))

        val result = repo.fetchNotifications()

        assertThat(result, empty())
    }

    @Test
    fun fetchNotifications_exception_returns_empty_and_logs() = runTest {
        whenever(api.getNotifications()).thenThrow(RuntimeException("Net Error"))

        val result = repo.fetchNotifications()

        assertThat(result, empty())
        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    // --- markAsRead ---

    @Test
    fun markAsRead_success_returns_true() = runTest {
        whenever(api.markAsRead("1")).thenReturn(Response.success(Unit))

        val result = repo.markAsRead("1")

        assertThat(result, `is`(true))
    }

    @Test
    fun markAsRead_failure_returns_false() = runTest {
        whenever(api.markAsRead("1")).thenReturn(Response.error(400, "".toResponseBody(null)))

        val result = repo.markAsRead("1")

        assertThat(result, `is`(false))
    }

    @Test
    fun markAsRead_exception_returns_false_and_logs() = runTest {
        whenever(api.markAsRead("1")).thenThrow(RuntimeException("Error"))

        val result = repo.markAsRead("1")

        assertThat(result, `is`(false))
        mockedLog.verify { Log.e(any(), any(), any()) }
    }
}
