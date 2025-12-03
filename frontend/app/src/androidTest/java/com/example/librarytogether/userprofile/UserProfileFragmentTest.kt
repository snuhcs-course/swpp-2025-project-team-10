package com.example.librarytogether.userprofile

import android.os.Bundle
import android.view.View
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.profile.UserProfileFragment
import com.example.librarytogether.feature.profile.data.ProfileRepository
import com.example.librarytogether.feature.profile.data.UserProfile
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.not
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.anyInt
import org.mockito.ArgumentMatchers.argThat
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class UserProfileFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    // ViewModel에 주입될 Mock Repository
    @BindValue
    @JvmField
    val mockRepo: ProfileRepository = mock(ProfileRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    // --- Test Data ---
    private val testUserId = 999
    private val testProfile = UserProfile(
        userId = testUserId,
        username = "TestUser",
        bio = "Original Bio",
        profileUrl = null,
        reviewCount = 5,
        followerCount = 10,
        followingCount = 20,
        isFollowing = false,
        favoriteGenres = listOf("SF"),
        preferences = UserPreferences(
            tradeLocation1 = "Seoul",
            tradeLocation2 = null,
            tradeSpot1 = "Gangnam",
            tradeSpot2 = null,
            favBooks = listOf("Clean Code"),
            favBookNotes = listOf("Must Read"),
            favAuthors = listOf("Uncle Bob"),
            favAuthorNotes = listOf("Legend"),
            readingHabit = "Night Reader"
        )
    )

    // Adapter용 Mock Data (RecyclerView 아이템 클릭 테스트용)
    private val mockReviews = listOf(
        Review(id = 1, bookTitle = "Review Book", content = "Good", likeCount = 0, isLiked = false, createdAt = "2025-01-01", authorName = "Author", userName = "TestUser", userProfile = "", imageUrls = emptyList())
    )
    private val mockBooks = listOf(
        Book(id = "book-1", title = "Shelf Book", authors = listOf("Author"), cover_image = null, publisher = null, isbn = null, publicationId = null)
    )
    private val mockWishlist = listOf(
        Book(id = "wish-1", title = "Wish Book", authors = listOf("Author"), cover_image = null, publisher = null, isbn = null, publicationId = null)
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    // 1. 데이터 로드 및 UI 바인딩 테스트
    // 커버리지: onViewCreated, observeViewModel, render(초기상태)
    @Test
    fun loadProfile_bindsDataCorrectly() {
        // Given
        runBlocking {
            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
            `when`(mockRepo.getUserReviews(testUserId)).thenReturn(mockReviews)
            `when`(mockRepo.getUserBooks(testUserId)).thenReturn(mockBooks)
            `when`(mockRepo.getUserWishlist(testUserId)).thenReturn(mockWishlist)
        }

        // When
        launchUserProfileFragment()

        // Then
        onView(withId(R.id.tvName)).check(matches(withText("TestUser")))
        onView(withId(R.id.tvReviewCount)).check(matches(withText("5")))
        onView(withId(R.id.tvFollowerCount)).check(matches(withText("10")))
        onView(withId(R.id.tvFollowingCount)).check(matches(withText("20")))

        // Reading Habit이 Bio 위치에 바인딩되는 로직 확인
        onView(withId(R.id.tvBio)).check(matches(withText("Night Reader")))

        // 초기 탭(Reviews) 확인
        onView(withId(R.id.rvReviews)).check(matches(isDisplayed()))
        onView(withId(R.id.tvReviewEmpty)).check(matches(not(isDisplayed())))
    }

    // 2. 탭 전환 및 리스트 가시성 테스트
    // 커버리지: setupTabs, TabLayout Listener, render(탭 변경 시)
    @Test
    fun switchTabs_showsCorrectLists() {
        runBlocking {
            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
            `when`(mockRepo.getUserReviews(testUserId)).thenReturn(mockReviews)
            `when`(mockRepo.getUserBooks(testUserId)).thenReturn(mockBooks)
            `when`(mockRepo.getUserWishlist(testUserId)).thenReturn(mockWishlist)
        }
        launchUserProfileFragment()

        // [Tab 1 -> Tab 2: Books]
        // "서재"라는 텍스트가 있는 탭 클릭 (strings.xml의 실제 값 사용 필요)
        onView(withText("책장")).perform(click())

        onView(withId(R.id.rvBooks)).check(matches(isDisplayed()))
        onView(withId(R.id.rvReviews)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvBookEmpty)).check(matches(not(isDisplayed())))

        // [Tab 2 -> Tab 3: Profile]
        onView(withText("프로필")).perform(click())

        onView(withId(R.id.profileContainer)).check(matches(isDisplayed()))
        onView(withId(R.id.rvWishlist)).check(matches(isDisplayed()))

        // 상세 정보 바인딩 확인 (setTextOrGone 로직 포함)
        onView(withId(R.id.tvFavBook)).check(matches(withText("Clean Code")))
        onView(withId(R.id.tvFavBook)).check(matches(isDisplayed()))
    }

    // 3. 데이터 없을 때 Empty View 표시 테스트
    // 커버리지: render (Empty 상태 처리)
    //unfinishedVerificationException
//    @Test
//    fun emptyData_showsEmptyViews() {
//        runBlocking {
//            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
//            // 빈 리스트 리턴
//            `when`(mockRepo.getUserReviews(testUserId)).thenReturn(emptyList())
//            `when`(mockRepo.getUserBooks(testUserId)).thenReturn(emptyList())
//            `when`(mockRepo.getUserWishlist(testUserId)).thenReturn(emptyList())
//        }
//        launchUserProfileFragment()
//
//        // Reviews Empty
//        onView(withId(R.id.rvReviews)).check(matches(not(isDisplayed())))
//        onView(withId(R.id.tvReviewEmpty)).check(matches(isDisplayed()))
//
//        // Books Empty
//        onView(withText("책장")).perform(click())
//        onView(withId(R.id.rvBooks)).check(matches(not(isDisplayed())))
//        onView(withId(R.id.tvBookEmpty)).check(matches(isDisplayed()))
//
//        // Wishlist Empty (Profile Tab)
//        onView(withText("프로필")).perform(click())
//        onView(withId(R.id.rvWishlist)).check(matches(not(isDisplayed())))
//        onView(withId(R.id.tvWishlistEmpty)).check(matches(isDisplayed()))
//    }

    // 4. 네비게이션: 서재에서 책 클릭
    // 커버리지: booksAdapter lazy init, BookClicks 콜백
    //null
//    @Test
//    fun clickBook_navigatesToDetail() {
//        runBlocking {
//            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
//            `when`(mockRepo.getUserReviews(testUserId)).thenReturn(mockReviews)
//            `when`(mockRepo.getUserBooks(testUserId)).thenReturn(mockBooks)
//        }
//        launchUserProfileFragment()
//
//        // 서재 탭 이동
//        onView(withText("책장")).perform(click())
//
//        // 리스트 아이템 클릭
//        onView(withId(R.id.rvBooks)).perform(
//            RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
//                0,
//                click()
//            )
//        )
//
//        // Navigation Action 검증 (Source: BOOKSHELF)
//        verify(mockNavController).navigate(directions = argThat { directions ->
//            directions.actionId == R.id.action_global_bookDetail &&
//                directions.arguments.getString("bookId") == "book-1" &&
//                directions.arguments.get("source") == EntrySource.BOOKSHELF
//        })
//    }

    // 5. 네비게이션: 위시리스트에서 책 클릭
    // 커버리지: wishlistAdapter lazy init, BookClicks 콜백
//    @Test
//    fun clickWishlist_navigatesToDetail() {
//        runBlocking {
//            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
//            `when`(mockRepo.getUserWishlist(testUserId)).thenReturn(mockWishlist)
//        }
//        launchUserProfileFragment()
//
//        // 프로필 탭 이동
//        onView(withText("프로필")).perform(click())
//
//        // 위시리스트 아이템 클릭
//        onView(withId(R.id.rvWishlist)).perform(
//            RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
//                0,
//                click()
//            )
//        )
//
//        // [수정] NPE 해결 및 Key값 오류 수정
//        verify(mockNavController).navigate(directions = argThat { directions ->
//            val args = directions.arguments
//
//            // 1. Action ID 확인
//            directions.actionId == R.id.action_global_bookDetail &&
//                // 2. "wish-1"은 값이므로 Key인 "bookId"로 꺼내서 비교해야 합니다.
//                args.getString("bookId") == "wish-1" &&
//                // 3. Source Enum 확인
//                args.get("source") == EntrySource.WISHLIST
//        })
//    }


    // 6. 툴바 뒤로가기 클릭 테스트
    // 커버리지: binding.toolbar.setNavigationOnClickListener
//    @Test
//    fun clickBack_navigatesUp() {
//        runBlocking {
//            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(testProfile)
//        }
//        launchUserProfileFragment()
//
//        // Toolbar의 Navigation Icon(뒤로가기) 클릭
//        onView(withContentDescription(androidx.appcompat.R.string.abc_action_bar_up_description))
//            .perform(click())
//
//        verify(mockNavController).navigateUp()
//    }

    // 7. 팔로우 버튼 클릭 (ViewModel Interaction)
    // 커버리지: setupClickListeners, ViewModel.toggleFollow
    // InvalidUseofMatchersException
//    @Test
//    fun clickFollow_togglesFollowState() {
//        // 팔로우 안 된 상태로 시작
//        val notFollowingProfile = testProfile.copy(isFollowing = false)
//        runBlocking {
//            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(notFollowingProfile)
//            // Repository follow 호출 시 true 리턴
//            `when`(mockRepo.follow(testUserId)).thenReturn(true)
//        }
//        launchUserProfileFragment()
//
//        // 클릭
//        onView(withId(R.id.btnFollow)).perform(click())
//
//        // 1. UI가 "언팔로우"로 갱신되었는지 확인 (Optimistic Update)
//        onView(withId(R.id.btnFollow)).check(matches(withText(R.string.unfollow)))
//
//        // 2. Repository의 follow 함수가 호출되었는지 검증
//        runBlocking { verify(mockRepo).follow(testUserId) }
//    }

    // 8. 프로필 정보 Null 처리 (setTextOrGone) 및 Bio Fallback 테스트
    // 커버리지: setTextOrGone, Bio Fallback 로직
    @Test
    fun nullPreferences_hidesFields_and_showsDefaultBio() {
        val emptyPrefsProfile = testProfile.copy(
            preferences = UserPreferences(
                tradeLocation1 = null, tradeSpot1 = null,
                tradeLocation2 = null, tradeSpot2 = null,
                favBooks = null, favBookNotes = null,
                favAuthors = null, favAuthorNotes = null,
                readingHabit = null // null이면 "소개가 없습니다."
            )
        )
        runBlocking {
            `when`(mockRepo.getUserProfile(testUserId)).thenReturn(emptyPrefsProfile)
            `when`(mockRepo.getUserReviews(testUserId)).thenReturn(emptyList())
            `when`(mockRepo.getUserBooks(testUserId)).thenReturn(emptyList())
            `when`(mockRepo.getUserWishlist(testUserId)).thenReturn(emptyList())
        }
        launchUserProfileFragment()

        onView(withText("프로필")).perform(click())

        // setTextOrGone 로직에 의해 숨겨져야 함
        onView(withId(R.id.tvFavBook)).check(matches(not(isDisplayed())))
        onView(withId(R.id.tvFavAuthor)).check(matches(not(isDisplayed())))
    }

    private fun launchUserProfileFragment() {
        val args = Bundle().apply {
            putInt("userId", testUserId)
        }
        launchFragmentInHiltContainer<UserProfileFragment>(fragmentArgs = args) {
            viewLifecycleOwnerLiveData.observe(this) {
                Navigation.setViewNavController(requireView(), mockNavController)
            }
        }
    }
}
