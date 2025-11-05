package com.example.librarytogether.home

import com.example.librarytogether.feature.home.data.FeedResponse
import com.example.librarytogether.feature.home.data.HomeApi
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.LikeResponse
import com.example.librarytogether.feature.home.data.Post
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.contains
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import org.mockito.kotlin.mock
import retrofit2.Response


class HomeRepositoryTest {
    private lateinit var api: HomeApi
    private lateinit var repo: HomeRepository

    @Before
    fun setUp() {
        api = mock()
        repo = HomeRepository(api)
    }


    @Test
    fun getFeed_returns_list_on_200() = runTest {
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
        val body = FeedResponse(results = listOf(p1, p2))
        whenever(api.feed()).thenReturn(Response.success(body))

        val list = repo.getFeed()

        assertThat(list, hasSize(2))
        assertThat(list[0].id, equalTo(1))
        assertThat(list[1].id, equalTo(2))
    }

    @Test
    fun getFeed_returns_empty_on_200_with_null_body() = runTest {
        val resp: Response<FeedResponse> = Response.success(null)
        whenever(api.feed()).thenReturn(resp)

        val list = repo.getFeed()

        assertThat(list, empty())
    }

    @Test(expected = IllegalStateException::class)
    fun getFeed_throws_on_non_200() = runTest {
        whenever(api.feed()).thenReturn(Response.error(500, "x".toResponseBody()))

        repo.getFeed() // expect throw
    }

    @Test(expected = RuntimeException::class)
    fun getFeed_rethrows_on_exception() = runTest {
        whenever(api.feed()).thenThrow(RuntimeException("net"))

        repo.getFeed() // expect throw
    }

    @Test
    fun toggleLike_returns_post_on_200() = runTest {
        val liked = Post(
            id = 7,
            bookTitle = "BX",
            authorName = "AX",
            posterName = "UX",
            posterProfile = "",
            content = "CX",
            userBookId = 77,
            imageUrls = listOf("u1", "u2"),
            likeCount = 9,
            createdAt = "2025-10-10T00:00:00Z",
            isLiked = true
        )
        val body = LikeResponse(post = liked)
        whenever(api.togglePostLike(7)).thenReturn(Response.success(body))

        val post = repo.toggleLike(7)

        assertThat(post.id, equalTo(7))
        assertThat(post.isLiked, equalTo(true))
        assertThat(post.likeCount, equalTo(9))
        assertThat(post.imageUrls, contains("u1", "u2"))
    }

    @Test(expected = IllegalStateException::class)
    fun toggleLike_throws_when_200_but_body_is_null() = runTest {
        val resp: Response<LikeResponse> = Response.success(null)
        whenever(api.togglePostLike(1)).thenReturn(resp)

        repo.toggleLike(1) // expect throw
    }

    @Test(expected = IllegalStateException::class)
    fun toggleLike_throws_on_non_200() = runTest {
        whenever(api.togglePostLike(1)).thenReturn(Response.error(404, "x".toResponseBody()))

        repo.toggleLike(1) // expect throw
    }

    @Test(expected = RuntimeException::class)
    fun toggleLike_rethrows_on_exception() = runTest {
        whenever(api.togglePostLike(any())).thenThrow(RuntimeException("boom"))

        repo.toggleLike(99) // expect throw
    }

}
