package com.example.librarytogether.feature.profile

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.profile.data.ProfileRepository
import com.example.librarytogether.feature.profile.data.UserProfile
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.nullValue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: ProfileRepository
    private lateinit var vm: ProfileViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = ProfileViewModel(repo)
    }

    private fun createProfile(id: Int = 1, following: Boolean = false, followers: Int = 10) = UserProfile(
        userId = id, username = "U$id", bio = "Bio", profileUrl = null,
        isFollowing = following, followerCount = followers,
        favoriteGenres = emptyList(),
        preferences = UserPreferences(null, null, null, null, null, null, null, null, null)
    )

    // --- Load User Profile ---

    @Test
    fun loadUserProfile_success_loads_all_data() = runTest {
        val userId = 1
        val profile = createProfile(userId)
        val books = listOf(Book(id = "b1", title = "T", authors = "A", cover_image = null, publisher = null, isbn = null))
        val reviews = listOf(Review(1, "B", "A", "U", "", "C"))
        val wishlist = listOf(Book(id = "w1", title = "W", authors = "A", cover_image = null, publisher = null, isbn = null))

        whenever(repo.getUserProfile(userId)).thenReturn(profile)
        whenever(repo.getUserBooks(userId)).thenReturn(books)
        whenever(repo.getUserReviews(userId)).thenReturn(reviews)
        whenever(repo.getUserWishlist(userId)).thenReturn(wishlist)

        vm.loadUserProfile(userId)
        advanceUntilIdle()

        assertThat(vm.userProfile.getOrAwaitValue(), equalTo(profile))
        assertThat(vm.books.getOrAwaitValue(), hasSize(1))
        assertThat(vm.reviews.getOrAwaitValue(), hasSize(1))
        assertThat(vm.wishlist.getOrAwaitValue(), hasSize(1))
        assertThat(vm.loading.getOrAwaitValue(), `is`(false))
        assertThat(vm.error.value, nullValue())
    }

    @Test
    fun loadUserProfile_failure_sets_error() = runTest {
        whenever(repo.getUserProfile(1)).thenThrow(RuntimeException("Boom"))

        vm.loadUserProfile(1)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("Boom"))
        assertThat(vm.loading.getOrAwaitValue(), `is`(false))
    }

    // --- Toggle Follow ---

    @Test
    fun toggleFollow_follow_success_optimistic_update() = runTest {
        val profile = createProfile(1, following = false, followers = 10)
        whenever(repo.getUserProfile(1)).thenReturn(profile)
        whenever(repo.follow(1)).thenReturn(true)

        vm.loadUserProfile(1)
        advanceUntilIdle()

        vm.toggleFollow()
        var currentProfile = vm.userProfile.getOrAwaitValue()
        assertThat(currentProfile?.isFollowing, `is`(true))
        assertThat(currentProfile?.followerCount, `is`(11)) // +1

        advanceUntilIdle()

        currentProfile = vm.userProfile.getOrAwaitValue()
        assertThat(currentProfile?.isFollowing, `is`(true))
        verify(repo).follow(1)
    }

    @Test
    fun toggleFollow_unfollow_success() = runTest {
        val profile = createProfile(1, following = true, followers = 10)
        whenever(repo.getUserProfile(1)).thenReturn(profile)
        whenever(repo.unfollow(1)).thenReturn(true)

        vm.loadUserProfile(1)
        advanceUntilIdle()

        vm.toggleFollow()

        val currentProfile = vm.userProfile.getOrAwaitValue()
        assertThat(currentProfile?.isFollowing, `is`(false))
        assertThat(currentProfile?.followerCount, `is`(9)) // -1

        advanceUntilIdle()
        verify(repo).unfollow(1)
    }

    @Test
    fun toggleFollow_failure_rollbacks_state() = runTest {
        val profile = createProfile(1, following = false, followers = 10)
        whenever(repo.getUserProfile(1)).thenReturn(profile)
        whenever(repo.follow(1)).thenReturn(false)

        vm.loadUserProfile(1)
        advanceUntilIdle()

        vm.toggleFollow()
        advanceUntilIdle()

        val currentProfile = vm.userProfile.getOrAwaitValue()
        assertThat(currentProfile?.isFollowing, `is`(false))
        assertThat(currentProfile?.followerCount, `is`(10))
        assertThat(vm.error.getOrAwaitValue(), equalTo("팔로우 처리에 실패했습니다."))
    }

    // --- Refresh methods ---

    @Test
    fun refreshBooks_success() = runTest {
        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        val newBooks = listOf(Book(id="b2", title="T", authors="A", cover_image = null, publisher = null, isbn = null))
        whenever(repo.getUserBooks(1)).thenReturn(newBooks)

        vm.refreshBooks()
        advanceUntilIdle()

        assertThat(vm.books.getOrAwaitValue(), hasSize(1))
        assertThat(vm.books.getOrAwaitValue()[0].id, equalTo("b2"))
    }

    @Test
    fun refreshReviews_failure_sets_error() = runTest {
        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        whenever(repo.getUserReviews(1)).thenThrow(RuntimeException("Fail"))

        vm.refreshReviews()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("리뷰를 불러오는 데 실패했습니다."))
    }

    // --- Toggle Like ---

    @Test
    fun toggleLike_success_updates_review_list() = runTest {
        val r1 = Review(1, "B", "A", "U", "", "C", isLiked = false)
        whenever(repo.getUserReviews(1)).thenReturn(listOf(r1))

        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        val updatedR1 = r1.copy(isLiked = true)
        whenever(repo.toggleReviewLike(1)).thenReturn(updatedR1)

        vm.toggleLike(1)
        advanceUntilIdle()

        val reviews = vm.reviews.getOrAwaitValue()
        assertThat(reviews[0].isLiked, `is`(true))
    }

    @Test
    fun toggleLike_failure_sets_error() = runTest {
        val r1 = Review(1, "B", "A", "U", "", "C")
        whenever(repo.getUserReviews(1)).thenReturn(listOf(r1))
        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        whenever(repo.toggleReviewLike(1)).thenReturn(null)

        vm.toggleLike(1)
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("좋아요 처리에 실패했습니다."))
    }

    // --- Refresh Wishlist ---

    @Test
    fun refreshWishlist_success() = runTest {
        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        val newWishlist = listOf(Book(id="w2", title="Wish", authors="A", cover_image = null, publisher = null, isbn = null))
        whenever(repo.getUserWishlist(1)).thenReturn(newWishlist)

        vm.refreshWishlist()
        advanceUntilIdle()

        val wishlist = vm.wishlist.getOrAwaitValue()
        assertThat(wishlist, hasSize(1))
        assertThat(wishlist[0].id, equalTo("w2"))
        assertThat(vm.loading.getOrAwaitValue(), `is`(false))
    }

    @Test
    fun refreshWishlist_failure_sets_error() = runTest {
        whenever(repo.getUserProfile(1)).thenReturn(createProfile(1))
        vm.loadUserProfile(1)
        advanceUntilIdle()

        whenever(repo.getUserWishlist(1)).thenThrow(RuntimeException("Fail"))

        vm.refreshWishlist()
        advanceUntilIdle()

        assertThat(vm.error.getOrAwaitValue(), equalTo("위시리스트를 불러오는 데 실패했습니다."))
        assertThat(vm.loading.getOrAwaitValue(), `is`(false))
    }
}
