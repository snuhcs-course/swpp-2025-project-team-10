package com.example.librarytogether.feature.notification

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.notification.data.NotificationDto
import com.example.librarytogether.feature.notification.data.NotificationRepository
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class NotificationViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: NotificationRepository
    private lateinit var vm: NotificationViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = NotificationViewModel(repo)
    }

    private fun createNotification(id: String = "1", read: Boolean = false) = NotificationDto(
        id = id,
        title = "Title",
        body = "Body",
        created_at = "2025-01-01",
        is_read = read,
        deepLink = null,
        type = null,
        related_object_id = null
    )

    @Test
    fun load_success_updates_items_and_loading() = runTest {
        val list = listOf(createNotification("1"), createNotification("2"))
        whenever(repo.fetchNotifications()).thenReturn(list)

        vm.load()

        assertThat(vm.loading.getOrAwaitValue(), `is`(true)) // load() 시작 시 true 세팅됨

        advanceUntilIdle()

        val items = vm.items.getOrAwaitValue()
        assertThat(items, hasSize(2))
        assertThat(items[0].id, equalTo("1"))
        assertThat(vm.loading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun markAsRead_success_updates_local_item_status() = runTest {
        val item = createNotification("1", read = false)
        whenever(repo.fetchNotifications()).thenReturn(listOf(item))
        vm.load()
        advanceUntilIdle()

        whenever(repo.markAsRead("1")).thenReturn(true)

        vm.markAsRead(item)
        advanceUntilIdle()

        val items = vm.items.getOrAwaitValue()
        assertThat(items[0].is_read, `is`(true)) // 로컬 상태가 true로 변경되었는지 확인

        verify(repo).markAsRead("1")
    }

    @Test
    fun markAsRead_failure_does_not_update_local_item() = runTest {
        val item = createNotification("1", read = false)
        whenever(repo.fetchNotifications()).thenReturn(listOf(item))
        vm.load()
        advanceUntilIdle()

        whenever(repo.markAsRead("1")).thenReturn(false)

        vm.markAsRead(item)
        advanceUntilIdle()

        val items = vm.items.getOrAwaitValue()
        assertThat(items[0].is_read, `is`(false)) // 변경되지 않음
    }
}
