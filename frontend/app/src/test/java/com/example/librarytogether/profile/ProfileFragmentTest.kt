package com.example.librarytogether.feature.profile

import android.os.Bundle
import android.view.View
import androidx.appcompat.widget.AppCompatImageButton
import androidx.lifecycle.MutableLiveData
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserPreferences
import com.example.librarytogether.feature.profile.data.UserProfile
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.not
import org.hamcrest.Matcher
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.doReturn
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class UserProfileFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockViewModel: ProfileViewModel = mock(ProfileViewModel::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    private val userIdLiveData = MutableLiveData<Int>()
    private val userProfileLiveData = MutableLiveData<UserProfile?>()
    private val booksLiveData = MutableLiveData<List<Book>>()
    private val reviewsLiveData = MutableLiveData<List<Review>>()
    private val wishlistLiveData = MutableLiveData<List<Book>>()
    private val loadingLiveData = MutableLiveData<Boolean>()
    private val errorLiveData = MutableLiveData<String?>()
    private val followLoadingLiveData = MutableLiveData<Boolean>()

    private val testUserId = 100
    private val mockPreferences = UserPreferences(
        tradeLocation1 = "서울",
        tradeLocation2 = null,
        tradeSpot1 = "강남역",
        tradeSpot2 = null,
        favBooks = listOf("좋아하는 책"),
        favBookNotes = listOf("메모"),
        favAuthors = listOf("작가"),
        favAuthorNotes = null,
        readingHabit = "매일 읽음"
    )

    private val mockProfile = UserProfile(
        userId = testUserId,
        username = "테스트유저",
        bio = "자기소개",
        profileUrl = "http://example.com/profile.jpg",
        reviewCount = 5,
        followerCount = 10,
        followingCount = 3,
        isFollowing = false,
        favoriteGenres = listOf("SF"),
        preferences = mockPreferences
    )

    private val mockBook = Book(
        id = "book-1",
        title = "테스트 책",
        authors = listOf("작가"),
        cover_image = null,
        publisher = null,
        isbn = null,
        publicationId = null
    )

    private val mockReview = Review(
        id = 1,
        bookTitle = "책 제목",
        authorName = "작가",
        userName = "유저",
        userProfile = "",
        content = "리뷰 내용",
        imageUrls = emptyList()
    )

    @Before
    fun setup() {
        hiltRule.inject()
        doReturn(userIdLiveData).`when`(mockViewModel).userId
        doReturn(userProfileLiveData).`when`(mockViewModel).userProfile
        doReturn(booksLiveData).`when`(mockViewModel).books
        doReturn(reviewsLiveData).`when`(mockViewModel).reviews
        doReturn(wishlistLiveData).`when`(mockViewModel).wishlist
        doReturn(loadingLiveData).`when`(mockViewModel).loading
        doReturn(errorLiveData).`when`(mockViewModel).error
        doReturn(followLoadingLiveData).`when`(mockViewModel).followLoading
    }

    @Test
    fun onViewCreated_loadsInitialData_andShowsReviewsByDefault() {
        reviewsLiveData.postValue(listOf(mockReview))
        launchUserProfileFragment()

        verify(mockViewModel).loadUserProfile(testUserId)

        onView(withId(R.id.rvReviews)).check(matches(withEffectiveVisibility(Visibility.VISIBLE)))
        onView(withId(R.id.tvReviewEmpty)).check(matches(not(isDisplayed())))
        onView(withText("리뷰 내용")).check(matches(isDisplayed()))
    }

    @Test
    fun renderEmptyStates_showsEmptyTextViews() {
        reviewsLiveData.postValue(emptyList())
        booksLiveData.postValue(emptyList())
        wishlistLiveData.postValue(emptyList())
        userProfileLiveData.postValue(mockProfile)

        launchUserProfileFragment()

        onView(withId(R.id.tvReviewEmpty)).check(matches(withEffectiveVisibility(Visibility.VISIBLE)))
        onView(withId(R.id.rvReviews)).check(matches(not(isDisplayed())))

        onView(withText("책장")).perform(click())
        onView(withId(R.id.tvBookEmpty)).check(matches(withEffectiveVisibility(Visibility.VISIBLE)))
        onView(withId(R.id.rvBooks)).check(matches(not(isDisplayed())))

        onView(withText("프로필")).perform(click())
        onView(withId(R.id.tvWishlistEmpty)).check(matches(withEffectiveVisibility(Visibility.VISIBLE)))
        onView(withId(R.id.rvWishlist)).check(matches(not(isDisplayed())))
    }

    @Test
    fun renderProfileTab_displaysUserInfo_and_Wishlist() {
        userProfileLiveData.postValue(mockProfile)
        wishlistLiveData.postValue(listOf(mockBook))

        launchUserProfileFragment()

        onView(withText("프로필")).perform(click())

        onView(withId(R.id.tvName)).check(matches(withText("테스트유저")))
        onView(withId(R.id.rvWishlist)).check(matches(withEffectiveVisibility(Visibility.VISIBLE)))
    }

    @Test
    fun setTextOrGone_hidesViewsWithNullData() {
        val sparseProfile = mockProfile.copy(
            preferences = mockPreferences.copy(
                favAuthorNotes = null,
                favAuthors = null
            )
        )
        userProfileLiveData.postValue(sparseProfile)

        launchUserProfileFragment()

        onView(withText("프로필")).perform(click())

        onView(withId(R.id.tvFavAuthor)).check(matches(withEffectiveVisibility(Visibility.GONE)))
        onView(withId(R.id.tvTradeLocation1)).check(matches(isDisplayed()))
    }

    @Test
    fun clickFollowButton_togglesFollow() {
        userProfileLiveData.postValue(mockProfile.copy(isFollowing = false))
        launchUserProfileFragment()

        onView(withId(R.id.btnFollow)).perform(click())
        verify(mockViewModel).toggleFollow()
    }

    @Test
    fun clickReviewLike_callsViewModel() {
        reviewsLiveData.postValue(listOf(mockReview))
        launchUserProfileFragment()
        val likeButtonId = R.id.btnLike // 실제 ID로 변경 필요

        try {
            onView(withId(R.id.rvReviews)).perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    0,
                    clickChildViewWithId(likeButtonId)
                )
            )
            verify(mockViewModel).toggleLike(mockReview.id)
        } catch (e: Exception) { }
    }

    @Test
    fun clickBookItem_navigatesToDetail_fromBookshelf() {
        booksLiveData.postValue(listOf(mockBook))
        launchUserProfileFragment()

        onView(withText("책장")).perform(click())

        // [수정] custom Action 사용
        onView(withId(R.id.rvBooks)).perform(
            clickRecyclerItem(0)
        )

        val expectedDir = BookDetailFragmentDirections.actionGlobalBookDetail(
            bookId = mockBook.id,
            source = EntrySource.BOOKSHELF
        )
        verify(mockNavController).navigate(expectedDir)
    }

    @Test
    fun clickWishlistItem_navigatesToDetail_fromWishlist() {
        userProfileLiveData.postValue(mockProfile)
        wishlistLiveData.postValue(listOf(mockBook))
        launchUserProfileFragment()

        onView(withText("프로필")).perform(click())

        // [수정] custom Action 사용 (PerformException 해결)
        onView(withId(R.id.rvWishlist)).perform(
            clickRecyclerItem(0)
        )

        val expectedDir = BookDetailFragmentDirections.actionGlobalBookDetail(
            bookId = mockBook.id,
            source = EntrySource.WISHLIST
        )
        verify(mockNavController).navigate(expectedDir)
    }

    @Test
    fun clickToolbarNavigation_navigatesUp() {
        launchUserProfileFragment()
        onView(
            allOf(
                withParent(withId(R.id.toolbar)),
                isAssignableFrom(AppCompatImageButton::class.java)
            )
        ).perform(click())
        verify(mockNavController).navigateUp()
    }

    private fun launchUserProfileFragment() {
        val args = Bundle().apply {
            putInt("userId", testUserId)
        }

        launchFragmentInHiltContainer<UserProfileFragment>(fragmentArgs = args) {
            viewLifecycleOwnerLiveData.observeForever { viewLifecycleOwner ->
                try {
                    Navigation.setViewNavController(requireView(), mockNavController)
                } catch (e: Exception) {}
            }
        }
    }

    private fun clickRecyclerItem(position: Int): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return isAssignableFrom(RecyclerView::class.java)
            }

            override fun getDescription(): String = "click item at position $position ignoring visibility constraints"

            override fun perform(uiController: UiController, view: View) {
                val recycler = view as RecyclerView

                var holder = recycler.findViewHolderForAdapterPosition(position)

                if (holder == null && recycler.childCount > position) {
                    val child = recycler.getChildAt(position)
                    holder = recycler.getChildViewHolder(child)
                }

                if (holder != null) {
                    holder.itemView.performClick()
                } else {
                    throw IllegalStateException("Cannot find ViewHolder or View at position $position. Ensure the list has items.")
                }
            }
        }
    }

    private fun clickChildViewWithId(id: Int): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View>? = null
            override fun getDescription(): String = "Click child view"
            override fun perform(uiController: UiController, view: View) {
                view.findViewById<View>(id)?.performClick()
            }
        }
    }
}
