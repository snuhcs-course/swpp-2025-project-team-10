package com.example.librarytogether.feature.comment

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.comment.data.CommentRepository
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

class CommentViewModelTest {

    @get:Rule val instant = InstantTaskExecutorRule()
    @get:Rule val dispatcher = MainDispatcherRule()

    private lateinit var repo: CommentRepository

    @Before
    fun setup() {
        repo = mock()
    }

    private fun vm() = CommentViewModel(repo)

    @Test
    fun initialize_sets_initialComments() = runTest {
        val initial = listOf(comment("c1"), comment("c2"))

        val vm = vm()
        vm.initialize(1, initial)

        val list = vm.comments.getOrAwaitValue()
        assertThat(list, hasSize(2))
    }

    @Test
    fun writeComment_updates_list() = runTest {
        val initial = listOf(comment("c1"))
        val updated = dummyPost(listOf(comment("c1"), comment("c2")))

        whenever(repo.writeComment(any(), any())).thenReturn(updated)

        val vm = vm()
        vm.initialize(1, initial)
        vm.writeComment("hi")
        advanceUntilIdle()

        val list = vm.comments.getOrAwaitValue()
        assertThat(list, hasSize(2))
    }

    @Test
    fun deleteComment_updates_list() = runTest {
        val initial = listOf(comment("c1"), comment("c2"))
        val updated = dummyPost(listOf(comment("c1")))

        whenever(repo.deleteComment(any(), any())).thenReturn(updated)

        val vm = vm()
        vm.initialize(1, initial)
        vm.deleteComment(initial[1])
        advanceUntilIdle()

        val list = vm.comments.getOrAwaitValue()
        assertThat(list, hasSize(1))
    }

    @Test
    fun toggleLike_updates_only_target_comment() = runTest {
        val c1 = comment("c1", 0, false)
        val c2 = comment("c2", 0, false)
        val updatedC2 = comment("c2", like = 10, liked = true)

        whenever(repo.toggleCommentLike(1, "c2")).thenReturn(updatedC2)

        val vm = vm()
        vm.initialize(1, listOf(c1, c2))
        vm.toggleLike(c2)
        advanceUntilIdle()

        val result = vm.comments.getOrAwaitValue()
        assertThat(result[1].likeCount, equalTo(10))
        assertThat(result[1].isLiked, equalTo(true))
    }

    private fun comment(
        id: String,
        like: Int = 0,
        liked: Boolean = false
    ) = CommentDto(
        id = id,
        authorName = "tester",
        authorProfile = null,
        content = "test",
        createdAt = "2025",
        updatedAt = "2025",
        likeCount = like,
        isLiked = liked
    )

    private fun dummyPost(list: List<CommentDto>) = Post(
        id = 1,
        posterId = 10,
        bookTitle = "t",
        authorName = "a",
        posterName = "user",
        posterProfile = "",
        content = "post",
        imageUrls = emptyList(),
        likeCount = 0,
        createdAt = "2025",
        isLiked = false,
        bookId = "b1",
        bookAvailableForBarter = false,
        posterLocation = null,
        comments = list
    )
}
