package com.example.librarytogether.diffutil

import com.example.librarytogether.feature.home.PostDiff
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.feature.library.BookDiff
import com.example.librarytogether.feature.library.ReviewDiff
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Test

class DiffTest {
    //PostDiff
    private val diff = PostDiff

    private fun base(id: Int = 1) = Post(
        id = id,
        posterId = 0,
        bookTitle = "B",
        authorName = "A",
        posterName = "U",
        posterProfile = "",
        content = "C",
        imageUrls = listOf("u1"),
        createdAt = "2025-01-01T00:00:00Z",
        userBookId = 11
    )

    @Test
    fun areItemsTheSame_sameId_true() {
        val o = base(id = 1)
        val n = base(id = 1)
        assertThat(diff.areItemsTheSame(o, n), equalTo(true))
    }

    @Test
    fun areItemsTheSame_diffId_false() {
        val o = base(id = 1)
        val n = base(id = 2)
        assertThat(diff.areItemsTheSame(o, n), equalTo(false))
    }

    @Test
    fun areContentsTheSame_sameObject_true() {
        val o = base()
        val n = o.copy(, 0,,,,,,)
        assertThat(diff.areContentsTheSame(o, n), equalTo(true))
    }

    @Test
    fun areContentsTheSame_likeCount_changed_false() {
        val o = base()
        val n = o.copy(, posterId = 0,,,,,, likeCount = 1,)
        assertThat(diff.areContentsTheSame(o, n), equalTo(false))
    }

    @Test
    fun areContentsTheSame_isLiked_changed_false() {
        val o = base()
        val n = o.copy(, posterId = 0,,,,,, isLiked = true,)
        assertThat(diff.areContentsTheSame(o, n), equalTo(false))
    }

    @Test
    fun areContentsTheSame_text_changed_false() {
        val o = base()
        val n = o.copy(, posterId = 0,,,,, content = "C2",)
        assertThat(diff.areContentsTheSame(o, n), equalTo(false))
    }

    @Test
    fun areContentsTheSame_images_order_changed_false() {
        val o = base().copy(, posterId = 0,,,,,, imageUrls = listOf("a", "b"),)
        val n = o.copy(, posterId = 0,,,,,, imageUrls = listOf("b", "a"),)
        // 순서가 바뀌면 UI가 달라지므로 false (순서 무시하려면 비교 로직을 set 비교로 바꿔야 함)
        assertThat(diff.areContentsTheSame(o, n), equalTo(false))
    }

    @Test
    fun areContentsTheSame_createdAt_changed_false() {
        val o = base()
        val n = o.copy(, posterId = 0,,,,,, createdAt = "2025-01-02T00:00:00Z",)
        assertThat(diff.areContentsTheSame(o, n), equalTo(false))
    }

    // ReviewDiff
    private fun sampleReview(id: Int = 1, liked: Boolean = false) =
        Review(
            id = id, bookTitle = "B", authorName = "A", userName = "U", userProfile = "",
            content = "C", createdAt = "2025-01-01T00:00:00Z", likeCount = if (liked) 1 else 0,
            isLiked = liked, imageUrls = emptyList()
        )

    @Test
    fun reviewDiff_id_and_contents() {
        val a = sampleReview(1, false)
        val b = sampleReview(1, false)
        val c = sampleReview(2, false)
        val d = sampleReview(1, true)

        assertThat(ReviewDiff.areItemsTheSame(a, b), equalTo(true))
        assertThat(ReviewDiff.areItemsTheSame(a, c), equalTo(false))

        assertThat(ReviewDiff.areContentsTheSame(a, b), equalTo(true))
        assertThat(ReviewDiff.areContentsTheSame(a, d), equalTo(false))
    }


    // BookDiff
    private fun sampleBook(id: Int = 1) = Book(
        id = id, title = "T$id", author = "A",
        coverUrl = null, publisher = null, isbn = null,
    )

    @Test
    fun bookDiff_id_and_contents() {
        val a = sampleBook(1)
        val b = sampleBook(1)
        val c = sampleBook(2)
        val d = sampleBook(1).copy(title = "다른 제목")

        assertThat(BookDiff.areItemsTheSame(a, b), equalTo(true))
        assertThat(BookDiff.areItemsTheSame(a, c), equalTo(false))

        assertThat(BookDiff.areContentsTheSame(a, b), equalTo(true))
        assertThat(BookDiff.areContentsTheSame(a, d), equalTo(false))
    }
}
