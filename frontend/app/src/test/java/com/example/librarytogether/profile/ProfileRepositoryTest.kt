package com.example.librarytogether.feature.profile

import android.util.Log
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.profile.data.ProfileApi
import com.example.librarytogether.feature.profile.data.ProfileRepository
import com.example.librarytogether.feature.profile.data.UserProfile
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.nullValue
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.MockedStatic
import org.mockito.Mockito.mockStatic
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileRepositoryTest {

    private lateinit var api: ProfileApi
    private lateinit var repo: ProfileRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = ProfileRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    // --- Helper ---
    private fun createProfile(id: Int = 1) = UserProfile(
        userId = id, username = "User$id", bio = "Hi", profileUrl = null,
        favoriteGenres = emptyList(),
        preferences = UserPreferences(null, null, null, null, null, null, null, null, null)
    )

    // --- getUserProfile ---

    @Test
    fun getUserProfile_success_returns_profile() = runTest {
        val profile = createProfile(1)
        whenever(api.getUserProfile(1)).thenReturn(Response.success(profile))

        val result = repo.getUserProfile(1)

        assertThat(result, equalTo(profile))
    }

    @Test
    fun getUserProfile_failure_returns_null_and_logs() = runTest {
        whenever(api.getUserProfile(1)).thenReturn(Response.error(404, "".toResponseBody(null)))

        val result = repo.getUserProfile(1)

        assertThat(result, nullValue())
        mockedLog.verify { Log.e(any(), any()) }
    }

    @Test
    fun getUserProfile_exception_returns_null_and_logs() = runTest {
        whenever(api.getUserProfile(1)).thenThrow(RuntimeException("Error"))

        val result = repo.getUserProfile(1)

        assertThat(result, nullValue())
        mockedLog.verify { Log.e(any(), any(), any()) }
    }

    // --- getUserBooks ---

    @Test
    fun getUserBooks_success_returns_list() = runTest {
        val books = listOf(Book(id = "1", title = "T", authors = "A", cover_image = null, publisher = null, isbn = null))
        whenever(api.getUserBooks(1)).thenReturn(Response.success(books))

        val result = repo.getUserBooks(1)

        assertThat(result, hasSize(1))
    }

    @Test
    fun getUserBooks_failure_returns_emptyList() = runTest {
        whenever(api.getUserBooks(1)).thenReturn(Response.error(500, "".toResponseBody(null)))

        val result = repo.getUserBooks(1)

        assertThat(result, empty())
    }

    // --- getUserReviews ---

    @Test
    fun getUserReviews_success_returns_list() = runTest {
        // Review 객체 생성 (필수 필드 채움)
        val review = Review(1, "B", "A", "U", "", "C")
        whenever(api.getUserReviews(1)).thenReturn(Response.success(listOf(review)))

        val result = repo.getUserReviews(1)

        assertThat(result, hasSize(1))
    }

    @Test
    fun getUserReviews_failure_returns_empty() = runTest {
        whenever(api.getUserReviews(1)).thenReturn(Response.error(404, "".toResponseBody(null)))
        val result = repo.getUserReviews(1)
        assertThat(result, empty())
    }

    // --- getUserWishlist ---

    @Test
    fun getUserWishlist_success_returns_list() = runTest {
        val books = listOf(Book(id = "1", title = "T", authors = "A", cover_image = null, publisher = null, isbn = null))
        whenever(api.getUserWishlist(1)).thenReturn(Response.success(books))

        val result = repo.getUserWishlist(1)

        assertThat(result, hasSize(1))
    }

    @Test
    fun getUserWishlist_failure_returns_empty() = runTest {
        whenever(api.getUserWishlist(1)).thenReturn(Response.error(500, "".toResponseBody(null)))
        val result = repo.getUserWishlist(1)
        assertThat(result, empty())
    }

    // --- Follow / Unfollow ---

    @Test
    fun follow_success_returns_true() = runTest {
        whenever(api.follow(1)).thenReturn(Response.success(Unit))
        assertThat(repo.follow(1), `is`(true))
    }

    @Test
    fun follow_failure_returns_false() = runTest {
        whenever(api.follow(1)).thenReturn(Response.error(400, "".toResponseBody(null)))
        assertThat(repo.follow(1), `is`(false))
    }

    @Test
    fun unfollow_success_returns_true() = runTest {
        whenever(api.unfollow(1)).thenReturn(Response.success(Unit))
        assertThat(repo.unfollow(1), `is`(true))
    }

    @Test
    fun unfollow_failure_returns_false() = runTest {
        whenever(api.unfollow(1)).thenReturn(Response.error(400, "".toResponseBody(null)))
        assertThat(repo.unfollow(1), `is`(false))
    }

    // --- Toggle Review Like ---

    @Test
    fun toggleReviewLike_success_returns_review() = runTest {
        val review = Review(1, "B", "A", "U", "", "C", isLiked = true)
        whenever(api.toggleReviewLike(1)).thenReturn(Response.success(review))

        val result = repo.toggleReviewLike(1)

        assertThat(result?.isLiked, `is`(true))
    }

    @Test
    fun toggleReviewLike_failure_returns_null() = runTest {
        whenever(api.toggleReviewLike(1)).thenReturn(Response.error(500, "".toResponseBody(null)))
        assertThat(repo.toggleReviewLike(1), nullValue())
    }
}
