package com.example.librarytogether.home

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.home.HomeViewModel
import com.example.librarytogether.feature.home.SortType
import com.example.librarytogether.feature.home.data.FeedResponse
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.LikeResponse
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.home.PostFixtures
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.CoreMatchers
import org.hamcrest.CoreMatchers.equalTo
import org.hamcrest.CoreMatchers.`is`
import org.hamcrest.MatcherAssert
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.CoreMatchers.notNullValue
import org.hamcrest.CoreMatchers.nullValue
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.emptyIterable
import org.hamcrest.Matchers.hasSize
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito
import org.mockito.Mockito.`when`
import org.mockito.junit.MockitoJUnitRunner

@RunWith(MockitoJUnitRunner::class)
class HomeViewModelTest {

    @get:Rule
    val instant = InstantTaskExecutorRule()
    @get:Rule
    val main = MainDispatcherRule()

    @Mock
    lateinit var repo: HomeRepository

    private fun vm() = HomeViewModel(repo)

    @Test
    fun loadFeed_success_populatesPosts_andStopsLoading() = runTest {
        // Given
        val p1 = PostFixtures.post(id = 1, likeCount = 1)
        val p2 = PostFixtures.post(id = 2, likeCount = 10)
        Mockito.`when`(repo.getFeed()).thenReturn(listOf(p2, p1))

        // When
        val vm = vm()
        advanceUntilIdle()

        // Then
        val list = vm.posts.getOrAwaitValue()
        // createdAt
        MatcherAssert.assertThat(list.first().id, CoreMatchers.`is`(p1.id))
        MatcherAssert.assertThat(vm.isLoading.getOrAwaitValue(), CoreMatchers.`is`(false))
        Mockito.verify(repo).getFeed()
    }

    @Test
    fun loadFeed_failure_setsError_andStopsLoading() = runTest {
        Mockito.`when`(repo.getFeed()).thenThrow(RuntimeException("boom"))

        val vm = vm()
        advanceUntilIdle()

        MatcherAssert.assertThat(vm.error.getOrAwaitValue(), CoreMatchers.`is`("네트워크 오류가 발생했습니다."))
        MatcherAssert.assertThat(vm.isLoading.getOrAwaitValue(), CoreMatchers.`is`(false))
    }

    @Test
    fun applySort_popular_sortsByLikeCountDescending() = runTest {
        val p1 = PostFixtures.post(id = 1, likeCount = 1)
        val p2 = PostFixtures.post(id = 2, likeCount = 10)
        Mockito.`when`(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()
        vm.applySort(SortType.POPULAR)

        val list = vm.posts.getOrAwaitValue()
        MatcherAssert.assertThat(list.first().id, CoreMatchers.`is`(p2.id))
    }

    @Test
    fun applySort_newest_sortsByCreatedAtDesc() = runTest {
        val p1 = PostFixtures.post(id = 1, likeCount = 1)
        val p2 = PostFixtures.post(id = 2, likeCount = 10)
        `when`(repo.getFeed()).thenReturn(listOf(p2, p1))

        val vm = vm()
        advanceUntilIdle()

        vm.applySort(SortType.LATEST)
        val list = vm.posts.getOrAwaitValue()
        assertThat(list.first().id, `is`(p1.id))
    }

    @Test
    fun applySort_switch_popular_then_newest_restores_latest_order() = runTest {
        val p1 = PostFixtures.post(id = 1, likeCount = 1)
        val p2 = PostFixtures.post(id = 2, likeCount = 10)
        `when`(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()

        vm.applySort(SortType.POPULAR)
        val popularOrderFirst = vm.posts.getOrAwaitValue().first().id
        assertThat(popularOrderFirst, `is`(p2.id))

        vm.applySort(SortType.LATEST)
        val newestOrderFirst = vm.posts.getOrAwaitValue().first().id
        assertThat(newestOrderFirst, `is`(p1.id))
    }

    @Test
    fun loadFeed_emptyList_setsEmptyPosts_andStopsLoading() = runTest {
        `when`(repo.getFeed()).thenReturn(emptyList())

        val vm = vm()
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        assertThat(list.isEmpty(), `is`(true))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun feedResponse_keeps_order_and_sets_defaults() {
        val p1 = Post(
            id = 1,
            bookTitle = "B1",
            authorName = "A1",
            posterName = "U1",
            posterProfile = "",
            content = "C1",
            userBookId = 11
        )
        val p2 = Post(
            id = 2,
            bookTitle = "B2",
            authorName = "A2",
            posterName = "U2",
            posterProfile = "",
            content = "C2",
            userBookId = 22
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
            bookTitle = "BX",
            authorName = "AX",
            posterName = "UX",
            posterProfile = "PX",
            content = "CX",
            userBookId = 77,
            imageUrls = listOf("u1", "u2"),
            likeCount = 9,
            createdAt = "2025-10-10T00:00:00Z",
            isLiked = true
        )

        val resp = LikeResponse(post = liked)

        assertThat(resp.post.id, equalTo(7))
        assertThat(resp.post.isLiked, equalTo(true))
        assertThat(resp.post.likeCount, equalTo(9))
        assertThat(resp.post.imageUrls, contains("u1", "u2"))
        assertThat(resp.post.bookTitle, equalTo("BX"))
        assertThat(resp.post.userBookId, equalTo(77))
    }

    @Test
    fun feedResponse_allows_empty_results() {
        val resp = FeedResponse(results = emptyList())
        assertThat(resp.results, emptyIterable())
    }


    @Test
    fun toggleLike_success_updatesOnlyTargetPost() = runTest {
        val p1 = PostFixtures.post(id = 1, liked = false, likeCount = 0)
        val p2 = PostFixtures.post(id = 2, liked = false, likeCount = 5)
        Mockito.`when`(repo.getFeed()).thenReturn(listOf(p1, p2))

        val vm = vm()
        advanceUntilIdle()

        val updated = p2.copy(isLiked = true, likeCount = p2.likeCount + 1)
        Mockito.`when`(repo.toggleLike(2)).thenReturn(updated)

        vm.toggleLike(p2)
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        val after1 = list.first { it.id == 1 }
        val after2 = list.first { it.id == 2 }
        MatcherAssert.assertThat(after1.isLiked, CoreMatchers.`is`(p1.isLiked))
        MatcherAssert.assertThat(after1.likeCount, CoreMatchers.`is`(p1.likeCount))
        MatcherAssert.assertThat(after2.isLiked, CoreMatchers.`is`(true))
        MatcherAssert.assertThat(after2.likeCount, CoreMatchers.`is`(p2.likeCount + 1))
        Mockito.verify(repo).toggleLike(2)
    }

    @Test
    fun toggleLike_failure_setsError_andKeepsPostsUnchanged() = runTest {
        val p1 = PostFixtures.post(id = 1, liked = false)
        Mockito.`when`(repo.getFeed()).thenReturn(listOf(p1))

        val vm = vm()
        advanceUntilIdle()

        Mockito.`when`(repo.toggleLike(1)).thenThrow(RuntimeException("boom"))
        vm.toggleLike(p1)
        advanceUntilIdle()

        val list = vm.posts.getOrAwaitValue()
        val after = list.first { it.id == 1 }
        MatcherAssert.assertThat(after.isLiked, CoreMatchers.`is`(false))
        MatcherAssert.assertThat(
            vm.error.getOrAwaitValue(),
            CoreMatchers.`is`("좋아요를 토글하는 데 실패했습니다.")
        )
    }
}
