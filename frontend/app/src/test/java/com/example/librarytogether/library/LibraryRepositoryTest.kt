package com.example.librarytogether.library

import com.example.librarytogether.feature.library.data.LibraryApi
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.ReviewResponse
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.feature.library.data.PostReview
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody
import org.hamcrest.CoreMatchers.`is`
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.InjectMocks
import org.mockito.Mock
import org.mockito.Mockito
import org.mockito.Mockito.`when`
import org.mockito.junit.MockitoJUnitRunner
import retrofit2.Response

@RunWith(MockitoJUnitRunner::class)
class LibraryRepositoryTest {

    @Mock
    private lateinit var libraryApi: LibraryApi // Repository가 의존하는 Api를 Mocking

    @InjectMocks
    private lateinit var repository: LibraryRepository // 테스트 대상

    // --- getMyReviews 테스트 ---

    @Test
    fun getMyReviews_success_returns_review_list() = runTest {
        // Arrange: API가 성공적으로 ReviewResponse를 반환하는 상황
        val fakeReview = LibraryFixtures.review(1)
        val fakeResponse = ReviewResponse(results = listOf(fakeReview))
        `when`(libraryApi.getMyReviews()).thenReturn(Response.success(fakeResponse))

        // Act
        val result = repository.getMyReviews()

        // Assert
        assertThat(result?.size, `is`(1))
        assertThat(result?.first()?.id, `is`(1))
    }

    @Test
    fun getMyReviews_api_failure_returns_empty_list() = runTest {
        // Arrange: API가 404 Not Found 같은 실패 응답을 보내는 상황
        `when`(libraryApi.getMyReviews()).thenReturn(Response.error(404, okhttp3.ResponseBody.create(null, "")))

        // Act
        val result = repository.getMyReviews()

        // Assert: Repository가 실패를 처리하고 빈 리스트를 반환하는지 검증
        assertThat(result?.size, `is`(0))
    }

    @Test
    fun getMyReviews_network_error_returns_empty_list() = runTest {
        // Arrange: 네트워크 오류 등으로 Exception이 발생하는 상황
        `when`(libraryApi.getMyReviews()).thenThrow(RuntimeException("Network Error"))

        // Act
        val result = repository.getMyReviews()

        // Assert: Repository가 Exception을 catch하고 빈 리스트를 반환하는지 검증
        assertThat(result?.size, `is`(0))
    }

    // --- toggleReviewLike 테스트 ---

    @Test
    fun toggleReviewLike_success_returns_updated_review() = runTest {
        // Arrange
        val updatedReview = LibraryFixtures.review(1, liked = true)
        `when`(libraryApi.toggleReviewLike(1)).thenReturn(Response.success(updatedReview))

        // Act
        val result = repository.toggleReviewLike(1)

        // Assert
        assertThat(result?.isLiked, `is`(true))
    }

    @Test
    fun toggleReviewLike_failure_returns_null() = runTest {
        // Arrange
        `when`(libraryApi.toggleReviewLike(1)).thenReturn(Response.error(500, okhttp3.ResponseBody.create(null, "")))

        // Act
        val result = repository.toggleReviewLike(1)

        // Assert
        assertThat(result, `is`(null as Review?))
    }

    // --- addReview 테스트 ---
    @Test
    fun addReview_calls_api_without_throwing_exception() = runTest {
        // Arrange
        val newReview = PostReview(bookTitle = "New Book", authorName = "New Author", publisher = "PUB", isbn = "ISBN", content = "New Content")

        try {
            repository.addReview(newReview)
        } catch (e: Exception) {
            throw AssertionError("addReview should not throw an exception on success", e)
        }

        // Assert: API의 addReview 함수가 올바른 파라미터로 호출되었는지 검증
        Mockito.verify(libraryApi).addReview(newReview)
    }

    // --- getMyBooks 테스트 ---
    @Test
    fun getMyBooks_success_returns_book_list() = runTest {
        // Arrange
        val fakeBooks = listOf(LibraryFixtures.book(1), LibraryFixtures.book(2))
        `when`(libraryApi.getMyBooks()).thenReturn(Response.success(fakeBooks))

        // Act
        val result = repository.getMyBooks()

        // Assert
        assertThat(result?.size, `is`(2))
    }

    @Test
    fun getMyBooks_api_failure_returns_empty_list() = runTest {
        // Arrange
        `when`(libraryApi.getMyBooks()).thenReturn(Response.error(404, ResponseBody.create(null, "")))

        // Act
        val result = repository.getMyBooks()

        // Assert
        assertThat(result?.size, `is`(0))
    }

    // --- getMyProfile 테스트 ---
    @Test
    fun getMyProfile_success_returns_user_profile() = runTest {
        // Arrange
        val fakeProfile = LibraryFixtures.profile(bio = "Test Bio")
        `when`(libraryApi.getMyProfile()).thenReturn(Response.success(fakeProfile))

        // Act
        val result = repository.getMyProfile()

        // Assert
        assertThat(result?.username, `is`("me"))
        assertThat(result?.bio, `is`("Test Bio"))
    }

    @Test
    fun getMyProfile_failure_returns_null() = runTest {
        // Arrange
        `when`(libraryApi.getMyProfile()).thenReturn(Response.error(404, ResponseBody.create(null, "")))

        // Act
        val result = repository.getMyProfile()

        // Assert
        assertThat(result, `is`(null as UserProfile?))
    }

    // --- updateMyProfile 테스트 ---
    @Test
    fun updateMyProfile_success_returns_updated_profile() = runTest {
        // Arrange
        val profileToUpdate = LibraryFixtures.profile()
        val updatedProfile = profileToUpdate.copy(bio = "Updated Bio")
        `when`(libraryApi.updateMyProfile(profileToUpdate)).thenReturn(Response.success(updatedProfile))

        // Act
        val result = repository.updateMyProfile(profileToUpdate)

        // Assert
        assertThat(result?.bio, `is`("Updated Bio"))
    }

    // --- getMyWishlist 테스트 ---
    @Test
    fun getMyWishlist_success_returns_book_list() = runTest {
        // Arrange
        val fakeWishlist = listOf(LibraryFixtures.book(3), LibraryFixtures.book(4))
        `when`(libraryApi.getMyWishlist()).thenReturn(Response.success(fakeWishlist))

        // Act
        val result = repository.getMyWishlist()

        // Assert
        assertThat(result?.size, `is`(2))
        assertThat(result?.first()?.id, `is`(3))
    }

    @Test
    fun getMyWishlist_api_failure_returns_empty_list() = runTest {
        // Arrange
        `when`(libraryApi.getMyWishlist()).thenReturn(Response.error(404, ResponseBody.create(null, "")))

        // Act
        val result = repository.getMyWishlist()

        // Assert
        assertThat(result?.size, `is`(0))
    }
}

