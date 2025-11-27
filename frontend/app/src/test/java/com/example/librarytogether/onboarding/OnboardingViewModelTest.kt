package com.example.librarytogether.feature.onboarding

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.example.librarytogether.feature.onboarding.data.LabelId
import com.example.librarytogether.feature.onboarding.data.OnboardingRepository
import com.example.librarytogether.testing.MainDispatcherRule
import com.example.librarytogether.testing.getOrAwaitValue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.containsInAnyOrder
import org.hamcrest.Matchers.empty
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasSize
import org.hamcrest.Matchers.`is`
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class OnboardingViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repo: OnboardingRepository
    private lateinit var vm: OnboardingViewModel

    @Before
    fun setUp() {
        repo = mock()
        vm = OnboardingViewModel(repo)
    }

    // --- Initial Load ---

    @Test
    fun loadInitial_sets_displayItems_from_books() = runTest {
        val books = listOf(LabelId(1, "B1"))
        whenever(repo.getBooks()).thenReturn(books)

        vm.loadInitial()
        advanceUntilIdle()

        val items = vm.displayItems.getOrAwaitValue()
        assertThat(items, hasSize(1))
        assertThat(items[0].name, equalTo("B1"))
        assertThat(vm.currentStep.getOrAwaitValue(), `is`(0))
    }

    // --- Selection Logic ---

    @Test
    fun toggleSelection_adds_and_removes_ids() {
        vm.toggleSelection(1, true)
        var selected = vm.selectedIds.getOrAwaitValue()
        assertThat(selected, contains(1))

        vm.toggleSelection(2, true)
        selected = vm.selectedIds.getOrAwaitValue()
        assertThat(selected, containsInAnyOrder(1, 2))

        vm.toggleSelection(1, false)
        selected = vm.selectedIds.getOrAwaitValue()
        assertThat(selected, contains(2))
    }

    @Test
    fun canProceed_is_true_only_when_3_or_more_selected() {
        assertThat(vm.canProceed.getOrAwaitValue(), `is`(false))

        vm.toggleSelection(1, true)
        vm.toggleSelection(2, true)
        assertThat(vm.canProceed.getOrAwaitValue(), `is`(false))

        vm.toggleSelection(3, true)
        assertThat(vm.canProceed.getOrAwaitValue(), `is`(true))

        vm.toggleSelection(3, false)
        assertThat(vm.canProceed.getOrAwaitValue(), `is`(false))
    }

    // --- Next Step Logic ---

    @Test
    fun nextStep_from_0_to_1_saves_and_loads_authors() = runTest {
        // Arrange: Step 0 (Books)
        val authors = listOf(LabelId(10, "A1"))
        whenever(repo.getAuthors()).thenReturn(authors)

        vm.toggleSelection(1, true) // Select ID 1

        // Act
        val finished = vm.nextStep()
        advanceUntilIdle()

        // Assert
        assertThat(finished, `is`(false)) // Not finished yet
        assertThat(vm.currentStep.getOrAwaitValue(), `is`(1)) // Next step
        assertThat(vm.selectedIds.getOrAwaitValue(), empty()) // Selection cleared

        val display = vm.displayItems.getOrAwaitValue()
        assertThat(display[0].name, equalTo("A1")) // Authors loaded

        verify(repo).saveSelection(eq(0), any()) // Saved step 0
    }

    @Test
    fun nextStep_from_1_to_2_saves_and_loads_genres() = runTest {
        whenever(repo.getAuthors()).thenReturn(emptyList()) // Dummy
        vm.nextStep()
        advanceUntilIdle()

        val genres = listOf(LabelId(20, "G1"))
        whenever(repo.getGenres()).thenReturn(genres)

        vm.toggleSelection(5, true)

        val finished = vm.nextStep()
        advanceUntilIdle()

        assertThat(finished, `is`(false))
        assertThat(vm.currentStep.getOrAwaitValue(), `is`(2))
        assertThat(vm.displayItems.getOrAwaitValue()[0].name, equalTo("G1"))

        verify(repo).saveSelection(eq(1), any())
    }

    @Test
    fun nextStep_from_2_submits_and_finishes() = runTest {
        whenever(repo.getAuthors()).thenReturn(emptyList())
        whenever(repo.getGenres()).thenReturn(emptyList())
        vm.nextStep()
        vm.nextStep()
        advanceUntilIdle()

        vm.toggleSelection(9, true) // Select ID 9 at Step 2
        whenever(repo.submitSelections()).thenReturn(true)

        val finished = vm.nextStep()
        advanceUntilIdle()

        assertThat(finished, `is`(true)) // Finished
        verify(repo).saveSelection(eq(2), any())
        verify(repo).submitSelections()
    }
}
