package com.example.librarytogether.feature

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

    // ---------- PostDiff ----------

    private val postDiff = PostDiff

    private fun basePost(
        id: Int = 1,
        posterId: Int = 10,
        bookTitle: String = "Book Title",
        authorName: String = "Author",
        posterName: String = "User",
        posterProfile: String = "profile.png",
        content: String = "Content",
        imageUrls: List<String> = emptyList(),
        likeCount: Int = 0,
        createdAt: String? = "2025-01-01T00:00:00Z",
        isLiked: Boolean = false,
        bookId: String = "uuid-1",
        bookAvailableForBarter: Boolean = true,
    ): Post = Post(
        id = id,
        posterId = posterId,
        bookTitle = bookTitle,
        authorName = authorName,
        posterName = posterName,
        posterProfile = posterProfile,
        content = content,
        imageUrls = imageUrls,
        likeCount = likeCount,
        createdAt = createdAt,
        isLiked = isLiked,
        bookId = bookId,
        bookAvailableForBarter = bookAvailableForBarter,
    )

    @Test
    fun post_areItemsTheSame_sameId_true() {
        val old = basePost(id = 1)
        val new = basePost(id = 1)
        assertThat(postDiff.areItemsTheSame(old, new), equalTo(true))
    }

    @Test
    fun post_areItemsTheSame_diffId_false() {
        val old = basePost(id = 1)
        val new = basePost(id = 2)
        assertThat(postDiff.areItemsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_sameData_true() {
        val old = basePost()
        val new = old.copy()
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(true))
    }

    @Test
    fun post_areContentsTheSame_likeCount_changed_false() {
        val old = basePost(likeCount = 0)
        val new = old.copy(likeCount = 1)
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_isLiked_changed_false() {
        val old = basePost(isLiked = false)
        val new = old.copy(isLiked = true)
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_content_changed_false() {
        val old = basePost(content = "C1")
        val new = old.copy(content = "C2")
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_imageUrls_changed_false() {
        val old = basePost(imageUrls = listOf("a", "b"))
        val new = old.copy(imageUrls = listOf("a", "b", "c"))
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_createdAt_changed_false() {
        val old = basePost(createdAt = "2025-01-01T00:00:00Z")
        val new = old.copy(createdAt = "2025-01-02T00:00:00Z")
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    @Test
    fun post_areContentsTheSame_bookAvailableForBarter_changed_false() {
        val old = basePost(bookAvailableForBarter = true)
        val new = old.copy(bookAvailableForBarter = false)
        assertThat(postDiff.areContentsTheSame(old, new), equalTo(false))
    }

    // ---------- ReviewDiff ----------

    private fun sampleReview(
        id: Int = 1,
        bookTitle: String = "Book Title",
        authorName: String = "Author",
        userName: String = "User",
        userProfile: String = "profile.png",
        content: String = "Content",
        imageUrls: List<String> = emptyList(),
        likeCount: Int = 0,
        createdAt: String? = "2025-01-01T00:00:00Z",
        isLiked: Boolean = false,
    ): Review = Review(
        id = id,
        bookTitle = bookTitle,
        authorName = authorName,
        userName = userName,
        userProfile = userProfile,
        content = content,
        imageUrls = imageUrls,
        likeCount = likeCount,
        createdAt = createdAt,
        isLiked = isLiked,
    )

    @Test
    fun reviewDiff_areItemsTheSame_sameId_true() {
        val a = sampleReview(id = 1)
        val b = sampleReview(id = 1)
        assertThat(ReviewDiff.areItemsTheSame(a, b), equalTo(true))
    }

    @Test
    fun reviewDiff_areItemsTheSame_diffId_false() {
        val a = sampleReview(id = 1)
        val b = sampleReview(id = 2)
        assertThat(ReviewDiff.areItemsTheSame(a, b), equalTo(false))
    }

    @Test
    fun reviewDiff_areContentsTheSame_sameData_true() {
        val a = sampleReview()
        val b = a.copy()
        assertThat(ReviewDiff.areContentsTheSame(a, b), equalTo(true))
    }

    @Test
    fun reviewDiff_areContentsTheSame_like_or_isLiked_changed_false() {
        val base = sampleReview(likeCount = 0, isLiked = false)
        val liked = base.copy(likeCount = 1, isLiked = true)

        assertThat(ReviewDiff.areContentsTheSame(base, liked), equalTo(false))
    }

    @Test
    fun reviewDiff_areContentsTheSame_content_changed_false() {
        val a = sampleReview(content = "A")
        val b = a.copy(content = "B")
        assertThat(ReviewDiff.areContentsTheSame(a, b), equalTo(false))
    }

    // ---------- BookDiff ----------

    private fun sampleBook(
        id: String = "1",
        title: String = "T$id",
        authors: String? = "Author",
        coverImage: String? = null,
        publisher: String? = null,
        isbn: String? = null,
    ): Book = Book(
        id = id,
        title = title,
        authors = authors,
        cover_image = coverImage,
        publisher = publisher,
        isbn = isbn,
    )

    @Test
    fun bookDiff_areItemsTheSame_sameId_true() {
        val a = sampleBook(id = "1")
        val b = sampleBook(id = "1")
        assertThat(BookDiff.areItemsTheSame(a, b), equalTo(true))
    }

    @Test
    fun bookDiff_areItemsTheSame_diffId_false() {
        val a = sampleBook(id = "1")
        val b = sampleBook(id = "2")
        assertThat(BookDiff.areItemsTheSame(a, b), equalTo(false))
    }

    @Test
    fun bookDiff_areContentsTheSame_sameData_true() {
        val a = sampleBook()
        val b = a.copy()
        assertThat(BookDiff.areContentsTheSame(a, b), equalTo(true))
    }

    @Test
    fun bookDiff_areContentsTheSame_title_changed_false() {
        val a = sampleBook(id = "1", title = "원래 제목")
        val b = a.copy(title = "다른 제목")
        assertThat(BookDiff.areContentsTheSame(a, b), equalTo(false))
    }
}
