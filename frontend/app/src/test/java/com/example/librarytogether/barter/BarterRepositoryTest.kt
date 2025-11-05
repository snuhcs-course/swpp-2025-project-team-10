package com.example.librarytogether.barter

import com.example.librarytogether.feature.barter.data.BarterApi
import com.example.librarytogether.feature.barter.data.BarterDetailResponse
import com.example.librarytogether.feature.barter.data.BarterOfferRequest
import com.example.librarytogether.feature.barter.data.BarterRepository
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.library.data.UserProfile
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.notNullValue
import org.hamcrest.Matchers.nullValue
import org.junit.Before
import org.junit.Test
import org.mockito.Mockito.mock
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import retrofit2.Response

class BarterRepositoryTest {
    private lateinit var api: BarterApi
    private lateinit var repo: BarterRepository

    @Before
    fun setUp() {
        api = mock()
        repo = BarterRepository(api)
    }

    // getBarterDetails

    @Test
    fun getBarterDetails_returns_body_on_200() = runTest {
        val book = Book(1, "T", "A", coverUrl = null, isbn = null, publisher = null)
        val body = BarterDetailResponse(
            book = book,
            owner = UserProfile(
                username = "u",
                profileUrl = "",
                bio = "",
                reviewCount = 0,
                followerCount = 0,
                followingCount = 0,
                favoriteGenres = emptyList(),
                preferences = UserPreferences(null, null, null, null, null, null, null, null, null)
            ),
            relatedReview = null
        )
        whenever(api.getBarterDetails(1)).thenReturn(Response.success(body))

        val res = repo.getBarterDetails(1)

        assertThat(res, notNullValue())
        assertThat(res?.book?.id, equalTo(1))
    }

    @Test
    fun getBarterDetails_returns_null_on_200_but_null_body() = runTest {
        whenever(api.getBarterDetails(1)).thenReturn(Response.success(null))

        val res = repo.getBarterDetails(1)

        assertThat(res, nullValue())
    }

    @Test
    fun getBarterDetails_returns_null_on_non_200() = runTest {
        whenever(api.getBarterDetails(1)).thenReturn(Response.error(500, "x".toResponseBody()))

        val res = repo.getBarterDetails(1)

        assertThat(res, nullValue())
    }

    @Test
    fun getBarterDetails_returns_null_on_exception() = runTest {
        whenever(api.getBarterDetails(1)).thenThrow(RuntimeException("net"))

        val res = repo.getBarterDetails(1)

        assertThat(res, nullValue())
    }

    // submitOffer

    @Test
    fun submitOffer_true_on_200() = runTest {
        whenever(api.submitOffer(any())).thenReturn(Response.success(Unit))

        val ok = repo.submitOffer(BarterOfferRequest(1, 2, "hi"))

        assertThat(ok, equalTo(true))
    }

    @Test
    fun submitOffer_false_on_non_200() = runTest {
        whenever(api.submitOffer(any())).thenReturn(Response.error(400, "x".toResponseBody()))

        val ok = repo.submitOffer(BarterOfferRequest(1, 2, "hi"))

        assertThat(ok, equalTo(false))
    }

    @Test
    fun submitOffer_false_on_exception() = runTest {
        whenever(api.submitOffer(any())).thenThrow(RuntimeException("boom"))

        val ok = repo.submitOffer(BarterOfferRequest(1, 2, "hi"))

        assertThat(ok, equalTo(false))
    }

    // getMyBooks

    @Test
    fun getMyBooks_returns_list_on_200() = runTest {
        val list = listOf(Book(1, "T", "A", null, null, null))
        whenever(api.getMyBooks()).thenReturn(Response.success(list))

        val res = repo.getMyBooks()

        assertThat(res, notNullValue())
        assertThat(res!!, contains(list[0]))
    }

    @Test
    fun getMyBooks_returns_null_on_200_but_null_body() = runTest {
        whenever(api.getMyBooks()).thenReturn(Response.success(null))

        val res = repo.getMyBooks()

        assertThat(res, nullValue())
    }

    @Test
    fun getMyBooks_returns_empty_on_non_200() = runTest {
        whenever(api.getMyBooks()).thenReturn(Response.error(404, "x".toResponseBody()))

        val res = repo.getMyBooks()

        assertThat(res, empty())
    }

    @Test
    fun getMyBooks_returns_empty_on_exception() = runTest {
        whenever(api.getMyBooks()).thenThrow(RuntimeException("net"))

        val res = repo.getMyBooks()

        assertThat(res, empty())
    }

    // getBookById

    @Test
    fun getBookById_returns_book_on_200() = runTest {
        val book = Book(9, "T9", "A9", null, null, null)
        whenever(api.getBookById(9)).thenReturn(Response.success(book))

        val res = repo.getBookById(9)

        assertThat(res?.id, equalTo(9))
    }

    @Test
    fun getBookById_returns_null_on_200_but_null_body() = runTest {
        whenever(api.getBookById(9)).thenReturn(Response.success(null))

        val res = repo.getBookById(9)

        assertThat(res, nullValue())
    }

    @Test
    fun getBookById_returns_null_on_non_200() = runTest {
        whenever(api.getBookById(9)).thenReturn(Response.error(500, "x".toResponseBody()))

        val res = repo.getBookById(9)

        assertThat(res, nullValue())
    }

    @Test
    fun getBookById_returns_null_on_exception() = runTest {
        whenever(api.getBookById(9)).thenThrow(RuntimeException("e"))

        val res = repo.getBookById(9)

        assertThat(res, nullValue())
    }

}
