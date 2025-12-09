package com.example.librarytogether.feature.search

import android.os.Looper
import android.view.KeyEvent
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.home.HomeViewModel
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.feature.search.data.SearchItem
import com.example.librarytogether.feature.search.data.SearchRepository
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.not
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.*
import org.robolectric.Shadows
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLooper
import org.robolectric.shadows.ShadowToast
import java.util.concurrent.TimeUnit

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class SearchFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockSearchRepo: SearchRepository = mock(SearchRepository::class.java)

    @BindValue
    @JvmField
    val mockHomeRepo: HomeRepository = mock(HomeRepository::class.java)

    private val mockNavController: NavController = mock(NavController::class.java)

    private val testSearchItem = SearchItem(
        id = "book-123",
        title = "테스트 검색 결과",
        author = "테스트 작가",
        publisher_name = "테스트 출판",
        isbn = "123456789",
        description = "설명",
        cover_image = null,
        is_for_barter = true
    )

    private val testPost = Post(
        id = 1,
        posterId = 10,
        bookTitle = "추천 책 제목",
        authorName = "작가",
        posterName = "유저",
        posterProfile = "",
        content = "내용",
        imageUrls = emptyList(),
        likeCount = 0,
        commentCount = 0,
        createdAt = "",
        isLiked = false,
        bookId = "book-rec",
        bookAvailableForBarter = true
    )

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun initialState_rendersCorrectly() {
        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
        }

        onView(withId(R.id.etSearch)).check(matches(withText("")))
        onView(withId(R.id.rvSearchResults)).check(matches(not(isDisplayed())))
        onView(withId(R.id.chipGroupRecommended)).check(matches(not(isDisplayed())))
    }

    @Test
    fun typingText_triggersSearch_afterDebounce() {
        // Given
        runBlocking {
            `when`(mockSearchRepo.search("hello")).thenReturn(listOf(testSearchItem))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
        }

        // When
        onView(withId(R.id.etSearch)).perform(typeText("hello"))

        ShadowLooper.idleMainLooper(350, TimeUnit.MILLISECONDS)

        // Then
        onView(withId(R.id.rvSearchResults)).check(matches(isDisplayed()))
        onView(allOf(withId(R.id.tvTitle), withText("테스트 검색 결과")))
            .check(matches(isDisplayed()))
    }

    @Test
    fun editorAction_triggersSearch_immediately() {
        runBlocking {
            `when`(mockSearchRepo.search("action")).thenReturn(listOf(testSearchItem))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
        }

        // When
        onView(withId(R.id.etSearch)).perform(replaceText("action"))
        onView(withId(R.id.etSearch)).perform(pressImeActionButton())

        ShadowLooper.idleMainLooper(100, TimeUnit.MILLISECONDS)

        // Then
        runBlocking {
            verify(mockSearchRepo, atLeastOnce()).search("action")
        }
        onView(allOf(withId(R.id.tvTitle), withText("테스트 검색 결과")))
            .check(matches(isDisplayed()))
    }

    @Test
    fun searchError_showsToast() {
        runBlocking {
            `when`(mockSearchRepo.search("error")).thenThrow(RuntimeException("Fail"))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
        }

        onView(withId(R.id.etSearch)).perform(replaceText("error"), pressImeActionButton())
        ShadowLooper.idleMainLooper(100, TimeUnit.MILLISECONDS)

        val latestToastText = ShadowToast.getTextOfLatestToast()
        assert(latestToastText == "검색 중 오류가 발생했습니다. 다시 시도해주세요.")
    }

    @Test
    fun pendingQuery_fromSharedViewModel_updatesUIAndSearches() {
        runBlocking {
            `when`(mockSearchRepo.search("pending")).thenReturn(listOf(testSearchItem))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
            val sharedVM = ViewModelProvider(requireActivity()).get(SearchSharedViewModel::class.java)
            sharedVM.setQuery("pending")
        }

        ShadowLooper.idleMainLooper(100, TimeUnit.MILLISECONDS)

        onView(withId(R.id.etSearch)).check(matches(withText("pending")))
        onView(allOf(withId(R.id.tvTitle), withText("테스트 검색 결과")))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recommendations_display_and_click_searches() {
        // Given
        runBlocking {
            `when`(mockHomeRepo.getFeed()).thenReturn(listOf(testPost))
            `when`(mockSearchRepo.search("추천 책 제목")).thenReturn(listOf(testSearchItem.copy(title = "추천 책 제목")))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
            val homeVM = ViewModelProvider(requireActivity()).get(HomeViewModel::class.java)
            // HomeViewModel 로드 트리거 (Context 필요할 수 있으므로 try-catch)
            try { homeVM.javaClass.getMethod("load").invoke(homeVM) } catch (e: Exception) {}
        }

        ShadowLooper.idleMainLooper(200, TimeUnit.MILLISECONDS)

        val chipMatcher = allOf(
            withText("추천 책 제목"),
            withParent(withId(R.id.chipGroupRecommended))
        )
        onView(chipMatcher).check(matches(isDisplayed()))
        onView(withId(R.id.tvRecommendedTitle)).check(matches(isDisplayed()))

        // When
        onView(chipMatcher).perform(click())

        ShadowLooper.idleMainLooper(200, TimeUnit.MILLISECONDS)

        // Then
        onView(withId(R.id.etSearch)).check(matches(withText("추천 책 제목")))

        onView(allOf(withId(R.id.tvTitle), withText("추천 책 제목")))
            .check(matches(isDisplayed()))

        onView(withId(R.id.chipGroupRecommended)).check(matches(not(isDisplayed())))
    }

    @Test
    fun clearText_showsRecommendations_clearsResults() {
        // Given
        runBlocking {
            `when`(mockHomeRepo.getFeed()).thenReturn(listOf(testPost))
            `when`(mockSearchRepo.search("query")).thenReturn(listOf(testSearchItem))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
            val homeVM = ViewModelProvider(requireActivity()).get(HomeViewModel::class.java)
            try { homeVM.javaClass.getMethod("load").invoke(homeVM) } catch (e: Exception) {}
        }

        ShadowLooper.idleMainLooper(300, TimeUnit.MILLISECONDS)

        onView(withId(R.id.chipGroupRecommended)).check(matches(isDisplayed()))

        onView(withId(R.id.etSearch)).perform(replaceText("query"), pressImeActionButton())

        ShadowLooper.idleMainLooper(300, TimeUnit.MILLISECONDS)

        onView(withId(R.id.rvSearchResults)).check(matches(isDisplayed()))
        onView(withId(R.id.chipGroupRecommended)).check(matches(not(isDisplayed())))

        //When
        onView(withId(R.id.etSearch)).perform(clearText())

        ShadowLooper.idleMainLooper(500, TimeUnit.MILLISECONDS)

        //Then
        onView(withId(R.id.rvSearchResults)).check(matches(not(isDisplayed())))

        onView(withId(R.id.chipGroupRecommended)).check(matches(isDisplayed()))
    }

    @Test
    fun clickResult_navigatesToDetail() {
        runBlocking {
            `when`(mockSearchRepo.search("nav")).thenReturn(listOf(testSearchItem))
        }

        launchFragmentInHiltContainer<SearchFragment> {
            Navigation.setViewNavController(requireView(), mockNavController)
        }

        onView(withId(R.id.etSearch)).perform(replaceText("nav"), pressImeActionButton())
        ShadowLooper.idleMainLooper(100, TimeUnit.MILLISECONDS)

        // When: Click Item
        onView(allOf(withId(R.id.tvTitle), withText("테스트 검색 결과"))).perform(click())

        // Then
        verify(mockNavController).navigate(
            BookDetailFragmentDirections.actionGlobalBookDetail(
                bookId = "book-123",
                source = EntrySource.SEARCH
            )
        )
    }
}
