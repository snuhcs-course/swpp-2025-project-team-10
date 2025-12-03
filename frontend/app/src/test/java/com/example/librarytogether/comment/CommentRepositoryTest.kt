package com.example.librarytogether.feature.comment

import com.example.librarytogether.feature.comment.data.CommentApi
import com.example.librarytogether.feature.comment.data.CommentDto
import com.example.librarytogether.feature.comment.data.CommentRepository
import com.example.librarytogether.feature.home.data.CommentLikeResponse
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.feature.home.data.PostResponse
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

class CommentRepositoryTest {

    private lateinit var api: CommentApi
    private lateinit var repo: CommentRepository

    @Before
    fun setup() {
        api = mock()
        repo = CommentRepository(api)
    }

    // ----------------------------------------
    // 댓글 작성
    // ----------------------------------------
    @Test
    fun writeComment_returns_updatedPost() = runTest {
        val updatedPost = dummyPost(
            comments = listOf(dummyComment("c1"), dummyComment("c2"))
        )

        whenever(api.createComment(any(), any()))
            .thenReturn(PostResponse(updatedPost))

        val result = repo.writeComment(1, "hello")

        assertThat(result.comments, hasSize(2))
        assertThat(result.comments[0].id, equalTo("c1"))
    }

    // ----------------------------------------
    // 댓글 삭제
    // ----------------------------------------
    @Test
    fun deleteComment_returns_updatedPost() = runTest {
        val updatedPost = dummyPost(
            comments = listOf(dummyComment("c1"))
        )

        whenever(api.deleteComment(any(), any()))
            .thenReturn(PostResponse(updatedPost))

        val result = repo.deleteComment(1, "c2")

        assertThat(result.comments, hasSize(1))
        assertThat(result.comments[0].id, equalTo("c1"))
    }

    // ----------------------------------------
    // 댓글 수정
    // ----------------------------------------
    @Test
    fun editComment_returns_updatedPost() = runTest {
        val updatedPost = dummyPost(
            comments = listOf(dummyComment("c1", content = "edited"))
        )

        whenever(api.editComment(any(), any(), any()))
            .thenReturn(PostResponse(updatedPost))

        val result = repo.editComment(1, "c1", "edited")

        assertThat(result.comments[0].content, equalTo("edited"))
    }

    // ----------------------------------------
    // 좋아요 / 취소
    // ----------------------------------------
    @Test
    fun toggleLike_returns_updatedComment() = runTest {
        val updatedComment = dummyComment(
            id = "c1",
            likeCount = 5,
            isLiked = true
        )

        whenever(api.toggleCommentLike(any(), any()))
            .thenReturn(CommentLikeResponse(updatedComment))

        val result = repo.toggleCommentLike(1, "c1")

        assertThat(result.like_count, equalTo(5))
        assertThat(result.isLiked, equalTo(true))
    }

    // ---------------- Helpers ----------------
    private fun dummyPost(comments: List<CommentDto>) = Post(
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
        comments = comments
    )

    private fun dummyComment(
        id: String,
        content: String = "hello",
        likeCount: Int = 0,
        isLiked: Boolean = false
    ) = CommentDto(
        id = id,
        authorName = "tester",
        authorProfile = null,
        content = content,
        createdAt = "2025",
        updatedAt = "2025",
        like_count = likeCount,
        isLiked = isLiked
    )
}
