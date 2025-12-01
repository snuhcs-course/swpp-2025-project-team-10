package com.example.librarytogether.feature.onboarding

import android.util.Log
import com.example.librarytogether.feature.onboarding.data.OnboardingApi
import com.example.librarytogether.feature.onboarding.data.OnboardingRepository
import com.example.librarytogether.feature.onboarding.data.OnboardingSubmitRequest
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.MockedStatic
import org.mockito.Mockito.mockStatic
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class OnboardingRepositoryTest {

    private lateinit var api: OnboardingApi
    private lateinit var repo: OnboardingRepository
    private lateinit var mockedLog: MockedStatic<Log>

    @Before
    fun setUp() {
        api = mock()
        mockedLog = mockStatic(Log::class.java)
        repo = OnboardingRepository(api)
    }

    @After
    fun tearDown() {
        mockedLog.close()
    }

    // --- Local Data Getters ---

    @Test
    fun getBooks_returns_fixed_list() {
        val books = repo.getBooks()
        assertThat(books, hasSize(5))
        assertThat(books[0].name, equalTo("해리포터"))
    }

    @Test
    fun getAuthors_returns_fixed_list() {
        val authors = repo.getAuthors()
        assertThat(authors, hasSize(5))
        assertThat(authors[0].name, equalTo("J.K. 롤링"))
    }

    @Test
    fun getGenres_returns_fixed_list() {
        val genres = repo.getGenres()
        assertThat(genres, hasSize(8))
        assertThat(genres[0].name, equalTo("현대소설"))
    }

    // --- submitSelections (Integration Logic) ---

    @Test
    fun submitSelections_success_sends_accumulated_ids_and_returns_true() = runTest {
        repo.saveSelection(0, listOf(1, 2)) // Books
        repo.saveSelection(1, listOf(3))    // Authors
        repo.saveSelection(2, listOf(4, 5)) // Genres

        whenever(api.submit(any())).thenReturn(Response.success(Unit))

        val result = repo.submitSelections()

        assertThat(result, `is`(true))

        val captor = argumentCaptor<OnboardingSubmitRequest>()
        verify(api).submit(captor.capture())
        val req = captor.firstValue

        assertThat(req.book_ids, contains(1, 2))
        assertThat(req.author_ids, contains(3))
        assertThat(req.genre_ids, contains(4, 5))
    }

    @Test
    fun submitSelections_failure_returns_false() = runTest {
        whenever(api.submit(any())).thenReturn(Response.error(400, "".toResponseBody(null)))

        val result = repo.submitSelections()

        assertThat(result, `is`(false))
    }

    @Test
    fun submitSelections_exception_returns_false_and_logs() = runTest {
        whenever(api.submit(any())).thenThrow(RuntimeException("Error"))

        val result = repo.submitSelections()

        assertThat(result, `is`(false))
        mockedLog.verify { Log.e(any(), any(), any()) }
    }

//    // --- saveSelection Logic Check ---
//    @Test
//    fun saveSelection_overwrites_previous_selection_for_same_step() = runTest {
//        repo.saveSelection(0, listOf(1, 2))
//
//        repo.saveSelection(0, listOf(3))
//
//        whenever(api.submit(any())).thenReturn(Response.success(Unit))
//        repo.submitSelections()
//
//        val captor = argumentCaptor<OnboardingSubmitRequest>()
//        verify(api).submit(captor.capture())
//
//        assertThat(captor.firstValue.book_ids, contains(3))
//    }
}
