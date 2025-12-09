package com.example.librarytogether.feature.onboarding

import android.content.Intent
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.RecyclerView
import androidx.test.core.app.ApplicationProvider
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.example.librarytogether.feature.main.MainActivity
import com.example.librarytogether.feature.onboarding.data.LabelId
import com.example.librarytogether.testing.launchFragmentInHiltContainer
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.not
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.doReturn
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class OnboardingFragmentTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockViewModel: OnboardingViewModel = mock(OnboardingViewModel::class.java)

    // LiveData Mocks
    private val displayItemsLiveData = MutableLiveData<List<LabelId>>()
    private val selectedIdsLiveData = MutableLiveData<Set<Int>>()
    private val currentStepLiveData = MutableLiveData<Int>()
    private val canProceedLiveData = MutableLiveData<Boolean>()

    // Dummy Data
    private val dummyItems = listOf(
        LabelId(1, "소설"),
        LabelId(2, "과학"),
        LabelId(3, "역사")
    )

    @Before
    fun setup() {
        hiltRule.inject()

        // ViewModel의 getter 프로퍼티 모킹 (doReturn 사용)
        doReturn(displayItemsLiveData).`when`(mockViewModel).displayItems
        doReturn(selectedIdsLiveData).`when`(mockViewModel).selectedIds
        doReturn(currentStepLiveData).`when`(mockViewModel).currentStep
        doReturn(canProceedLiveData).`when`(mockViewModel).canProceed
    }

    @Test
    fun onViewCreated_initializesCorrectly() {
        // Given
        currentStepLiveData.postValue(0)
        displayItemsLiveData.postValue(dummyItems)

        // When
        launchOnboardingFragment()

        // Then
        verify(mockViewModel).loadInitial()
        onView(withId(R.id.rvChips)).check(matches(isDisplayed()))
        onView(withText("소설")).check(matches(isDisplayed()))
    }

    @Test
    fun renderStep0_showsBooksTitle_andNextButton() {
        // Given
        currentStepLiveData.postValue(0)

        // When
        launchOnboardingFragment()

        // Then
        onView(withId(R.id.tvTitle)).check(matches(withText(R.string.onboarding_title_books)))
        onView(withId(R.id.btnNext)).check(matches(withText(R.string.next)))
    }

    @Test
    fun renderStep1_showsAuthorsTitle_andNextButton() {
        // Given
        currentStepLiveData.postValue(1)

        // When
        launchOnboardingFragment()

        // Then
        onView(withId(R.id.tvTitle)).check(matches(withText(R.string.onboarding_title_authors)))
        onView(withId(R.id.btnNext)).check(matches(withText(R.string.next)))
    }

    @Test
    fun renderStep2_showsGenresTitle_andDoneButton() {
        // Given
        currentStepLiveData.postValue(2)

        // When
        launchOnboardingFragment()

        // Then
        onView(withId(R.id.tvTitle)).check(matches(withText(R.string.onboarding_title_genres)))
        onView(withId(R.id.btnNext)).check(matches(withText(R.string.done)))
    }

    @Test
    fun observeCanProceed_enablesOrDisablesButton() {
        // Given
        canProceedLiveData.postValue(false)
        launchOnboardingFragment()

        // Then: Disabled
        onView(withId(R.id.btnNext)).check(matches(not(isEnabled())))

        // When: Enabled
        canProceedLiveData.postValue(true)

        // Then: Enabled
        onView(withId(R.id.btnNext)).check(matches(isEnabled()))
    }

    @Test
    fun clickNext_whenNotFinished_doesNotNavigate() = runBlocking {
        // Given
        currentStepLiveData.postValue(0)
        canProceedLiveData.postValue(true)

        // Mocking suspend function
        `when`(mockViewModel.nextStep()).thenReturn(false) // 아직 안 끝남

        launchOnboardingFragment()

        // When
        onView(withId(R.id.btnNext)).perform(click())

        // Then
        verify(mockViewModel).nextStep()

        // Verify Activity did NOT start
        val nextStartedActivity = shadowOf(ApplicationProvider.getApplicationContext<android.app.Application>()).nextStartedActivity
        assertEquals(null, nextStartedActivity)
    }

    @Test
    fun clickNext_whenFinished_navigatesToMain() = runBlocking {
        // Given
        currentStepLiveData.postValue(2) // 마지막 단계
        canProceedLiveData.postValue(true)

        // Mocking suspend function
        `when`(mockViewModel.nextStep()).thenReturn(true) // 끝남

        launchOnboardingFragment()

        // When
        onView(withId(R.id.btnNext)).perform(click())

        // Then
        verify(mockViewModel).nextStep()

        // Verify Activity Started (MainActivity)
        val nextStartedActivity = shadowOf(ApplicationProvider.getApplicationContext<android.app.Application>()).nextStartedActivity
        val expectedIntent = Intent(ApplicationProvider.getApplicationContext(), MainActivity::class.java)

        assertEquals(expectedIntent.component, nextStartedActivity.component)
        // Flag 확인 (CLEAR_TASK | NEW_TASK)
        val flags = nextStartedActivity.flags
        val expectedFlags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        assertEquals(expectedFlags, flags and expectedFlags)
    }

    private fun launchOnboardingFragment() {
        launchFragmentInHiltContainer<OnboardingFragment>()
    }
}
