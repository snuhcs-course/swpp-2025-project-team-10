package com.example.librarytogether.feature.library.data

import android.util.Log
import com.example.librarytogether.feature.library.LibraryFixtures
import com.example.librarytogether.feature.library.data.*
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.nullValue
import org.junit.After
import org.junit.Assert.assertThrows
import org.junit.Before
import org.junit.Test
import org.mockito.MockedStatic
import org.mockito.Mockito.mockStatic
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import retrofit2.Response

class LibraryRepositoryTest {

    private lateinit var libraryApi: LibraryApi
    private lateinit var mockedLog: MockedStatic<Log>
    private lateinit var repository: LibraryRepository

    @Before
    fun setup() {
        libraryApi = mock()

        mockedLog = mockStatic(Log::class.java)

        repository = LibraryRepository(libraryApi)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    private fun <T> errorResponse(code: Int = 404): Response<T> {
        return Response.error(code, "{}".toResponseBody("application/json".toMediaTypeOrNull()))
    }

    // --- getMyReviews 테스트 ---

    @Test
    fun getMyReviews_success_returns_list() = runTest {
        val reviews = listOf(LibraryFixtures.review(1))
        val response = ReviewResponse(reviews)
        whenever(libraryApi.getMyReviews()).thenReturn(Response.success(response))

        val result = repository.getMyReviews()

        assertThat(result, hasSize(1))
        assertThat(result?.get(0)?.id, equalTo(1))
    }

    @Test
    fun getMyReviews_failure_returns_empty_list_and_logs() = runTest {
        whenever(libraryApi.getMyReviews()).thenReturn(errorResponse())

        val result = repository.getMyReviews()

        assertThat(result, empty())
        mockedLog.verify { Log.e(any(), any()) }
    }

    @Test
    fun getMyReviews_exception_returns_empty_list() = runTest {
        whenever(libraryApi.getMyReviews()).thenThrow(RuntimeException("Network"))

        val result = repository.getMyReviews()

        assertThat(result, empty())
    }

    // --- addReview 테스트 ---

    @Test
    fun addReview_success_calls_api() = runTest {
        val review = LibraryFixtures.postReview()
        whenever(libraryApi.addReview(review)).thenReturn(Response.success(Unit))

        repository.addReview(review)

        verify(libraryApi).addReview(review)
    }

    @Test
    fun addReview_exception_logs_error() = runTest {
        val review = LibraryFixtures.postReview()
        whenever(libraryApi.addReview(review)).thenThrow(RuntimeException("Error"))

        repository.addReview(review)

        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    // --- toggleLike 테스트 ---

    @Test
    fun toggleLike_success_returns_review() = runTest {
        val review = LibraryFixtures.review(1, liked = true)
        val response = ReviewLikeResponse(review)
        whenever(libraryApi.toggleReviewLike(1)).thenReturn(Response.success(response))

        val result = repository.toggleLike(1)

        assertThat(result.isLiked, equalTo(true))
    }

    @Test
    fun toggleLike_failure_throws_exception() = runTest {
        whenever(libraryApi.toggleReviewLike(1)).thenReturn(errorResponse(500))

        assertThrows(IllegalStateException::class.java) {
            kotlinx.coroutines.test.runTest {
                repository.toggleLike(1)
            }
        }
    }

    // --- getMyBooks 테스트 ---

    @Test
    fun getMyBooks_success_returns_list() = runTest {
        val books = listOf(LibraryFixtures.book(1))
        whenever(libraryApi.getMyBooks()).thenReturn(Response.success(books))

        val result = repository.getMyBooks()

        assertThat(result, hasSize(1))
    }

    @Test
    fun getMyBooks_failure_returns_empty_list() = runTest {
        whenever(libraryApi.getMyBooks()).thenReturn(errorResponse())

        val result = repository.getMyBooks()

        assertThat(result, empty())
    }

    // --- addBook 테스트 ---

    @Test
    fun addBook_success_returns_true() = runTest {
        val book = PostBook("T", "A", null, null, false)
        // API 정의에 따라 Response<Unit> 혹은 Response<Book> 등 적절히 조정 필요
        whenever(libraryApi.addBook(book)).thenReturn(Response.success(Unit))

        val result = repository.addBook(book)

        assertThat(result, equalTo(true))
    }

    @Test
    fun addBook_failure_returns_false() = runTest {
        val book = PostBook("T", "A", null, null, false)
        whenever(libraryApi.addBook(book)).thenReturn(errorResponse())

        val result = repository.addBook(book)

        assertThat(result, equalTo(false))
        mockedLog.verify { Log.e(any(), any()) }
    }

    @Test
    fun addBook_exception_returns_false() = runTest {
        val book = PostBook("T", "A", null, null, false)
        whenever(libraryApi.addBook(book)).thenThrow(RuntimeException("Error"))

        val result = repository.addBook(book)

        assertThat(result, equalTo(false))
    }

    // --- searchBooks 테스트 ---

    @Test
    fun searchBooks_success_returns_list() = runTest {
        val books = listOf(LibraryFixtures.book(1))
        whenever(libraryApi.searchBooks("query")).thenReturn(Response.success(books))

        val result = repository.searchBooks("query")

        assertThat(result, hasSize(1))
    }

    @Test
    fun searchBooks_failure_returns_empty_list() = runTest {
        whenever(libraryApi.searchBooks("query")).thenReturn(errorResponse())

        val result = repository.searchBooks("query")

        assertThat(result, empty())
    }

    // --- getMyProfile 테스트 ---

    @Test
    fun getMyProfile_success_returns_profile() = runTest {
        val profile = LibraryFixtures.profile()
        whenever(libraryApi.getMyProfile()).thenReturn(Response.success(profile))

        val result = repository.getMyProfile()

        assertThat(result?.username, equalTo("me"))
    }

    @Test
    fun getMyProfile_failure_returns_null() = runTest {
        whenever(libraryApi.getMyProfile()).thenReturn(errorResponse())

        val result = repository.getMyProfile()

        assertThat(result, nullValue())
    }

    // --- updateMyProfile 테스트 ---

    @Test
    fun updateMyProfile_success_returns_profile() = runTest {
        val profile = LibraryFixtures.profile()
        whenever(libraryApi.updateMyProfile(profile)).thenReturn(Response.success(profile))

        val result = repository.updateMyProfile(profile)

        assertThat(result?.username, equalTo("me"))
    }

    @Test
    fun updateMyProfile_failure_returns_null() = runTest {
        val profile = LibraryFixtures.profile()
        whenever(libraryApi.updateMyProfile(profile)).thenReturn(errorResponse())

        val result = repository.updateMyProfile(profile)

        assertThat(result, nullValue())
    }

    // --- addToWishlist 테스트 ---

    @Test
    fun addToWishlist_success_returns_true() = runTest {
        val book = LibraryFixtures.book(1)
        whenever(libraryApi.addToWishlist(any())).thenReturn(Response.success(Unit))

        val result = repository.addToWishlist(book)

        assertThat(result, equalTo(true))
    }

    @Test
    fun addToWishlist_failure_returns_false() = runTest {
        val book = LibraryFixtures.book(1)
        whenever(libraryApi.addToWishlist(any())).thenReturn(errorResponse())

        val result = repository.addToWishlist(book)

        assertThat(result, equalTo(false))
    }

    // --- addToWishlistById 테스트 ---

    @Test
    fun addToWishlistById_success_returns_true() = runTest {
        whenever(libraryApi.addToWishlistById("id")).thenReturn(Response.success(Unit))

        val result = repository.addToWishlistById("id")

        assertThat(result, equalTo(true))
    }

    @Test
    fun addToWishlistById_exception_returns_false() = runTest {
        whenever(libraryApi.addToWishlistById("id")).thenThrow(RuntimeException("Error"))

        val result = repository.addToWishlistById("id")

        assertThat(result, equalTo(false))
    }

    // --- removeFromWishlistById 테스트 ---

    @Test
    fun removeFromWishlistById_success_returns_true() = runTest {
        whenever(libraryApi.removeFromWishlistById("id")).thenReturn(Response.success(Unit))

        val result = repository.removeFromWishlistById("id")

        assertThat(result, equalTo(true))
    }

    // --- getMyWishlist 테스트 ---

    @Test
    fun getMyWishlist_success_returns_list() = runTest {
        val books = listOf(LibraryFixtures.book(1), LibraryFixtures.book(2))
        whenever(libraryApi.getMyWishlist()).thenReturn(Response.success(books))

        val result = repository.getMyWishlist()

        assertThat(result, hasSize(2))
        assertThat(result?.get(0)?.id, equalTo("1"))
    }

    @Test
    fun getMyWishlist_failure_returns_empty_list_and_logs() = runTest {
        val errorBody = "{}".toResponseBody("application/json".toMediaTypeOrNull())
        whenever(libraryApi.getMyWishlist()).thenReturn(Response.error(404, errorBody))

        val result = repository.getMyWishlist()

        assertThat(result, empty())
        mockedLog.verify { Log.e(any(), any()) }
    }

    @Test
    fun getMyWishlist_exception_returns_empty_list_and_logs() = runTest {
        whenever(libraryApi.getMyWishlist()).thenThrow(RuntimeException("Network Error"))

        val result = repository.getMyWishlist()

        assertThat(result, empty()) // 빈 리스트 반환 확인
        mockedLog.verify { Log.e(any(), any(), any()) } // 로그 호출 확인
    }
}
