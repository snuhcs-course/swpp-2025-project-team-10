package com.example.librarytogether.library

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.library.LibraryViewModel
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.PostBook
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.CoreMatchers.`is`
import org.hamcrest.CoreMatchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito
import org.mockito.Mockito.verify
import org.mockito.Mockito.verifyNoMoreInteractions
import org.mockito.Mockito.`when`
import org.mockito.junit.MockitoJUnitRunner
import org.mockito.kotlin.whenever

@RunWith(MockitoJUnitRunner::class)
class LibraryViewModelTest {

    @get:Rule
    val instant = InstantTaskExecutorRule()
    @get:Rule val main = MainDispatcherRule()

    @Mock
    lateinit var repo: LibraryRepository

    private fun createVM() = LibraryViewModel(repo)

    @Test
    fun init_loadsReviewsBooksProfileWishlist_andStopsLoading() = runTest {
        // Arrange
        val r1 = LibraryFixtures.review(1)
        val r2 = LibraryFixtures.review(2, likeCount = 10)
        val b1 = LibraryFixtures.book(1)
        val b2 = LibraryFixtures.book(2)
        val prof = LibraryFixtures.profile()
        val wish = listOf(b1)

        `when`(repo.getMyReviews()).thenReturn(listOf(r1, r2))
        `when`(repo.getMyBooks()).thenReturn(listOf(b1, b2))
        `when`(repo.getMyProfile()).thenReturn(prof)
        `when`(repo.getMyWishlist()).thenReturn(wish)

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.myReviews.getOrAwaitValue().size, `is`(2))
        assertThat(vm.myBooks.getOrAwaitValue().size, `is`(2))
        assertThat(vm.userProfile.getOrAwaitValue()?.username, `is`("me"))
        assertThat(vm.myWishlist.getOrAwaitValue().size, `is`(1))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    // --- Reviews ---

    @Test
    fun refreshMyReviews_success_populatesList_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyReviews()).thenReturn(listOf(LibraryFixtures.review(1)))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.myReviews.getOrAwaitValue().size, `is`(1))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
        verify(repo).getMyReviews()
    }

    @Test
    fun refreshMyReviews_failure_setsError_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyReviews()).thenThrow(RuntimeException("boom"))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("네트워크 오류가 발생했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun refreshMyReviews_repoReturnsNull_setsEmptyList() = runTest {
        // Arrange: Repository가 성공적으로 응답했으나 Body가 null인 상황을 시뮬레이션
        `when`(repo.getMyReviews()).thenReturn(null)

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert: ViewModel이 null을 빈 리스트로 잘 처리하는지 검증
        val reviews = vm.myReviews.getOrAwaitValue()
        assertThat(reviews, `is`(emptyList()))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun refreshMyBooks_repoReturnsNull_setsEmptyList() = runTest {
        // Arrange
        `when`(repo.getMyBooks()).thenReturn(null)

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        val books = vm.myBooks.getOrAwaitValue()
        assertThat(books, `is`(emptyList()))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun refreshWishlist_repoReturnsNull_setsEmptyList() = runTest {
        // Arrange
        `when`(repo.getMyWishlist()).thenReturn(null)

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        val wishlist = vm.myWishlist.getOrAwaitValue()
        assertThat(wishlist, `is`(emptyList()))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }
    // --- Books ---

    @Test
    fun refreshMyBooks_success_populatesList_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyBooks()).thenReturn(listOf(LibraryFixtures.book(1)))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.myBooks.getOrAwaitValue().size, `is`(1))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
        verify(repo).getMyBooks()
    }

    @Test
    fun refreshMyBooks_failure_setsError_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyBooks()).thenThrow(RuntimeException("boom"))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("책장 목록을 불러오는 데 실패했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun refreshMyBooks_throwsException_setsError() = runTest {
        `when`(repo.getMyBooks()).thenThrow(RuntimeException("Network Error"))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert: 에러 메시지가 올바르게 설정되었는지 검증
        val error = vm.error.getOrAwaitValue()
        assertThat(error, `is`("책장 목록을 불러오는 데 실패했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun addNewBook_success_refresh_and_navigate() = runTest {
        val post = PostBook(title = "T", author = "A", publisher = null, isbn = null, isForBarter = true)
        val newBookList =
            listOf(Book(id = 1, title = "T", author = "A", publisher = null, isbn = null, coverUrl = null))

        `when`(repo.addBook(post)).thenReturn(true)
        `when`(repo.getMyBooks()).thenReturn(newBookList)

        val vm = createVM()
        // init {}
        advanceUntilIdle()

        // Act
        vm.addNewBook(post)
        advanceUntilIdle()

        // Assert
        assertThat(vm.myBooks.getOrAwaitValue().size, `is`(1))
        assertThat(vm.navigateToLibrary.getOrAwaitValue(), `is`(true))

        vm.onBookAddedNavigationComplete()

        // Assert 2
        assertThat(vm.navigateToLibrary.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun addNewBook_failure_sets_error() = runTest {
        // Arrange
        val post = PostBook("T", "A", null, null, true)
        `when`(repo.addBook(post)).thenReturn(false)

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.addNewBook(post)
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("책 추가에 실패했습니다."))
    }

    @Test
    fun addNewBook_exception_sets_error() = runTest {
        // Arrange
        val post = PostBook("T", "A", null, null, true)
        `when`(repo.addBook(post)).thenThrow(RuntimeException("boom"))

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.addNewBook(post)
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("책 추가 중 오류가 발생했습니다."))
    }

    @Test
    fun refreshWishlist_throwsException_setsError() = runTest {
        // Arrange
        `when`(repo.getMyWishlist()).thenThrow(RuntimeException("Network Error"))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        val error = vm.error.getOrAwaitValue()
        assertThat(error, `is`("위시리스트를 불러오는 데 실패했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }
    // --- Wishlist ---

    @Test
    fun refreshWishlist_success_populatesList_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyWishlist()).thenReturn(listOf(LibraryFixtures.book(1)))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.myWishlist.getOrAwaitValue().size, `is`(1))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
        verify(repo).getMyWishlist()
    }

    @Test
    fun refreshWishlist_failure_setsError_andStopsLoading() = runTest {
        // Arrange
        `when`(repo.getMyWishlist()).thenThrow(RuntimeException("boom"))

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("위시리스트를 불러오는 데 실패했습니다."))
        assertThat(vm.isLoading.getOrAwaitValue(), `is`(false))
    }

    // --- Profile ---

    @Test
    fun loadProfile_success_setsUserProfile() = runTest {
        // Arrange
        `when`(repo.getMyProfile()).thenReturn(LibraryFixtures.profile())

        // Act
        val vm = createVM()
        advanceUntilIdle()

        // Assert
        assertThat(vm.userProfile.getOrAwaitValue()?.username, `is`("me"))
        // loadProfile() 자체는 isLoading 토글 안 함
    }

    @Test
    fun saveProfile_success_updatesUserProfile() = runTest {
        // Arrange
        val newProf = LibraryFixtures.profile().copy(bio = "updated")
        `when`(repo.updateMyProfile(newProf)).thenReturn(newProf)

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.saveProfile(newProf)
        advanceUntilIdle()

        // Assert
        assertThat(vm.userProfile.getOrAwaitValue()?.bio, `is`("updated"))
        verify(repo).updateMyProfile(newProf)
    }

    @Test
    fun saveProfile_failure_setsError() = runTest {
        // Arrange
        val newProf = LibraryFixtures.profile().copy(bio = "updated")
        `when`(repo.updateMyProfile(newProf)).thenThrow(RuntimeException("boom"))

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.saveProfile(newProf)
        advanceUntilIdle()

        // Assert
        assertThat(vm.error.getOrAwaitValue(), `is`("프로필 저장에 실패했습니다."))
    }

    @Test
    fun saveProfile_throwsException_setsError() = runTest {
        // Arrange
        val profileToSave = LibraryFixtures.profile()
        `when`(repo.updateMyProfile(profileToSave)).thenThrow(RuntimeException("Network Error"))

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.saveProfile(profileToSave)
        advanceUntilIdle()

        // Assert
        val error = vm.error.getOrAwaitValue()
        assertThat(error, `is`("프로필 저장에 실패했습니다."))
    }

    // --- Add review ---

    @Test
    fun addNewReview_callsRepository_andRefreshesReviews() = runTest {
        // Arrange
        val pr = LibraryFixtures.postReview()
        `when`(repo.getMyReviews()).thenReturn(emptyList())

        val vm = createVM()
        advanceUntilIdle()

        // Act
        vm.addNewReview(pr)
        advanceUntilIdle()

        // Assert
        verify(repo).addReview(pr)
        verify(repo, Mockito.times(2)).getMyReviews()
//        verify(repo).getMyReviews()
    }

    // --- Toggle like ---

    @Test
    fun toggleLike_success_updatesOnlyThatReview() = runTest {
        // Arrange
        val r1 = LibraryFixtures.review(1, liked = false, likeCount = 0)
        val r2 = LibraryFixtures.review(2, liked = false, likeCount = 5)
        `when`(repo.getMyReviews()).thenReturn(listOf(r1, r2))
        val vm = createVM()
        advanceUntilIdle()

        val updated = r2.copy(isLiked = true, likeCount = r2.likeCount + 1)
        `when`(repo.toggleReviewLike(2)).thenReturn(updated)

        // Act
        vm.toggleLike(r2)
        advanceUntilIdle()

        // Assert
        val list = vm.myReviews.getOrAwaitValue()
        val after1 = list.first { it.id == 1 }
        val after2 = list.first { it.id == 2 }
        assertThat(after1.isLiked, `is`(false))
        assertThat(after1.likeCount, `is`(0))
        assertThat(after2.isLiked, `is`(true))
        assertThat(after2.likeCount, `is`(6))
        verify(repo).toggleReviewLike(2)
    }

    @Test
    fun toggleLike_failure_setsError_andKeepsListUnchanged() = runTest {
        // Arrange
        val r1 = LibraryFixtures.review(1, liked = false)
        `when`(repo.getMyReviews()).thenReturn(listOf(r1))
        val vm = createVM()
        advanceUntilIdle()
        `when`(repo.toggleReviewLike(1)).thenReturn(null) // 실패 경로

        // Act
        vm.toggleLike(r1)
        advanceUntilIdle()

        // Assert
        val list = vm.myReviews.getOrAwaitValue()
        assertThat(list.first().isLiked, `is`(false))
        assertThat(vm.error.getOrAwaitValue(), `is`("좋아요 처리에 실패했습니다."))
    }

    @Test
    fun onErrorShown_resetsErrorToNull() = runTest {
        val vm = createVM()
        vm.onErrorShown()
        assertThat(vm.error.getOrAwaitValue(), `is`(null as String?))
        verifyNoMoreInteractions(repo)
    }
}
