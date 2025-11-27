package com.example.librarytogether.feature.home

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.home.data.FeedResponse
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.LikeResponse
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.emptyIterable
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.nullValue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: HomeRepository

    @Before
    fun setUp() {
        repo = mock()
    }

    private fun vm() = HomeViewModel(repo)

    @Test
    fun loadFeed_success_populatesPosts_andStopsLoading_sortedByLatest() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            likeCount = 1,
            createdAt = "2025-01-02T00:00:00Z"
        )
        val p2 = PostFixtures.post(
            id = 2,
            likeCount = 10,
            createdAt = "2025-01-01T00:00:00Z"
        )
        whenever(repo.getFeed()).thenReturn(listOf(p2, p1))

        val vm = vm()
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        assertThat(list.first().id, equalTo(p1.id))
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
        verify(repo).getFeed()
    }

    @Test
    fun loadFeed_failure_setsError_andStopsLoading() = runTest {
        whenever(repo.getFeed()).thenThrow(RuntimeException("boom"))

        val vm = vm()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("네트워크 오류가 발생했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
    }

    @Test
    fun applySort_popular_sortsByLikeCountDescending() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            likeCount = 1,
            createdAt = "2025-01-01T00:00:00Z"
        )
        val p2 = PostFixtures.post(
            id = 2,
            likeCount = 10,
            createdAt = "2025-01-01T00:00:00Z"
        )
        whenever(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()

        vm.applySort(SortType.POPULAR)
        val list = vm.posts.getOrAwaitValue()
        assertThat(list.first().id, equalTo(p2.id))
    }

    @Test
    fun applySort_latest_sortsByCreatedAtDesc() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            createdAt = "2025-01-02T00:00:00Z"
        )
        val p2 = PostFixtures.post(
            id = 2,
            createdAt = "2025-01-01T00:00:00Z"
        )
        whenever(repo.getFeed()).thenReturn(listOf(p2, p1))

        val vm = vm()
        advanceUntilIdle()

        vm.applySort(SortType.LATEST)
        val list = vm.posts.getOrAwaitValue()
        assertThat(list.first().id, equalTo(p1.id))
    }

    @Test
    fun applySort_switch_popular_then_latest_restores_latest_order() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            likeCount = 1,
            createdAt = "2025-01-02T00:00:00Z"
        )
        val p2 = PostFixtures.post(
            id = 2,
            likeCount = 10,
            createdAt = "2025-01-01T00:00:00Z"
        )
        whenever(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()

        vm.applySort(SortType.POPULAR)
        val popularFirst = vm.posts.getOrAwaitValue().first().id
        assertThat(popularFirst, equalTo(p2.id))

        vm.applySort(SortType.LATEST)
        val latestFirst = vm.posts.getOrAwaitValue().first().id
        assertThat(latestFirst, equalTo(p1.id))
    }

    @Test
    fun loadFeed_emptyList_setsEmptyPosts_andStopsLoading() = runTest {
        whenever(repo.getFeed()).thenReturn(emptyList())

        val vm = vm()
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        assertThat(list, emptyIterable())
        assertThat(vm.isLoading.getOrAwaitValue(), equalTo(false))
    }

    @Test
    fun feedResponse_keeps_order_and_sets_defaults() {
        val p1 = Post(
            id = 1,
            posterId = 10,
            bookTitle = "B1",
            authorName = "A1",
            posterName = "U1",
            posterProfile = "",
            content = "C1",
            bookId = "book-11",
            bookAvailableForBarter = true
        )
        val p2 = Post(
            id = 2,
            posterId = 20,
            bookTitle = "B2",
            authorName = "A2",
            posterName = "U2",
            posterProfile = "",
            content = "C2",
            bookId = "book-22",
            bookAvailableForBarter = true
        )

        val resp = FeedResponse(results = listOf(p1, p2))

        assertThat(resp.results, hasSize(2))
        assertThat(resp.results[0].id, equalTo(1))
        assertThat(resp.results[1].id, equalTo(2))

        val d1 = resp.results[0]
        assertThat(d1.imageUrls, emptyIterable())
        assertThat(d1.likeCount, equalTo(0))
        assertThat(d1.createdAt, nullValue())
        assertThat(d1.isLiked, equalTo(false))
    }

    @Test
    fun likeResponse_wraps_post_and_preserves_flags() {
        val liked = Post(
            id = 7,
            posterId = 77,
            bookTitle = "BX",
            authorName = "AX",
            posterName = "UX",
            posterProfile = "PX",
            content = "CX",
            imageUrls = listOf("u1", "u2"),
            likeCount = 9,
            createdAt = "2025-10-10T00:00:00Z",
            isLiked = true,
            bookId = "book-77",
            bookAvailableForBarter = false
        )

        val resp = LikeResponse(post = liked)

        assertThat(resp.post.id, equalTo(7))
        assertThat(resp.post.isLiked, equalTo(true))
        assertThat(resp.post.likeCount, equalTo(9))
        assertThat(resp.post.imageUrls, contains("u1", "u2"))
        assertThat(resp.post.bookTitle, equalTo("BX"))
        assertThat(resp.post.bookId, equalTo("book-77"))
    }

    @Test
    fun feedResponse_allows_empty_results() {
        val resp = FeedResponse(results = emptyList())
        assertThat(resp.results, emptyIterable())
    }

    @Test
    fun toggleLike_success_updatesOnlyTargetPost() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            likeCount = 0,
            liked = false
        )
        val p2 = PostFixtures.post(
            id = 2,
            likeCount = 5,
            liked = false
        )

        whenever(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()

        val updated = p2.copy(
            likeCount = p2.likeCount + 1,
            isLiked = true
        )
        whenever(repo.toggleLike(2)).thenReturn(updated)

        vm.toggleLike(p2)
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        val after1 = list.first { it.id == 1 }
        val after2 = list.first { it.id == 2 }

        assertThat(after1.isLiked, equalTo(p1.isLiked))
        assertThat(after1.likeCount, equalTo(p1.likeCount))
        assertThat(after2.isLiked, equalTo(true))
        assertThat(after2.likeCount, equalTo(p2.likeCount + 1))

        verify(repo).toggleLike(2)
    }

    @Test
    fun toggleLike_failure_setsError_andKeepsPostsUnchanged() = runTest {
        val p1 = PostFixtures.post(
            id = 1,
            likeCount = 0,
            liked = false
        )
        whenever(repo.getFeed()).thenReturn(listOf(p1))

        val vm = vm()
        advanceUntilIdle()

        whenever(repo.toggleLike(1)).thenThrow(RuntimeException("boom"))

        vm.toggleLike(p1)
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        val after = list.first { it.id == 1 }
        assertThat(after.isLiked, equalTo(false))
        assertThat(vm.error.getOrAwaitValue(), equalTo("좋아요를 토글하는 데 실패했습니다."))
    }

    // --- requestBarter 테스트 ---

    @Test
    fun requestBarter_success_sets_barterSuccess_true() = runTest {
        val ownerId = 10
        val bookId = "book-uuid"
        whenever(repo.createRequest(ownerId, bookId)).thenReturn(true)

        val vm = vm()
        vm.requestBarter(ownerId, bookId)
        advanceUntilIdle()

        assertThat(vm.barterSuccess.getOrAwaitValue(), equalTo(true))
        assertThat(vm.barterError.value, nullValue())
        verify(repo).createRequest(ownerId, bookId)
    }

    @Test
    fun requestBarter_failure_sets_barterError() = runTest {
        val ownerId = 10
        val bookId = "book-uuid"
        whenever(repo.createRequest(ownerId, bookId)).thenReturn(false)

        val vm = vm()
        vm.requestBarter(ownerId, bookId)
        advanceUntilIdle()

        assertThat(vm.barterSuccess.getOrAwaitValue(), equalTo(false))
        assertThat(vm.barterError.getOrAwaitValue(), equalTo("교환 신청에 실패했습니다."))
    }

    @Test
    fun requestBarter_exception_sets_barterError() = runTest {
        val ownerId = 10
        val bookId = "book-uuid"
        whenever(repo.createRequest(ownerId, bookId)).thenThrow(RuntimeException("Network Fail"))

        val vm = vm()
        vm.requestBarter(ownerId, bookId)
        advanceUntilIdle()

        assertThat(vm.barterError.getOrAwaitValue(), equalTo("Network Fail"))
    }
}

