package com.example.librarytogether.feature.onboarding

import androidx.lifecycle.*
import com.example.librarytogether.feature.onboarding.data.LabelId
import com.example.librarytogether.feature.onboarding.data.OnboardingRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val repo: OnboardingRepository
) : ViewModel() {

    private val _currentStep = MutableLiveData(0)
    val currentStep: LiveData<Int> = _currentStep
    private val _displayItems = MutableLiveData<List<LabelId>>(emptyList())
    val displayItems: LiveData<List<LabelId>> = _displayItems
    private val _selected = MutableLiveData<Set<Int>>(emptySet())
    val selectedIds: LiveData<List<Int>> = _selected.map { it.toList() }

    val canProceed: LiveData<Boolean> = _selected.map { it.size >= 3 }

    fun toggleSelection(id: Int, isSelected: Boolean) {
        // Create a new set to ensure LiveData emits a new value and UI updates.
        val currentSet = _selected.value ?: emptySet()
        val newSet = if (isSelected) {
            currentSet + id // Creates a new set with the added item
        } else {
            currentSet - id // Creates a new set with the removed item
        }
        _selected.value = newSet
    }

    // Loads the initial list of books.
    fun loadInitial() {
        viewModelScope.launch {
            _displayItems.value = repo.getBooks()
        }
    }
    suspend fun nextStep(): Boolean {
        val currentStepValue = _currentStep.value ?: 0
        val currentSelectedIds = _selected.value?.toList() ?: emptyList()

        // Save the current selection before moving on.
        repo.saveSelection(currentStepValue, currentSelectedIds)

        return if (currentStepValue < 2) {
            val nextStep = currentStepValue + 1
            // Reset state for the next step.
            _selected.value = emptySet()
            _currentStep.value = nextStep
            // Load new items for the next step.
            _displayItems.value = when (nextStep) {
                1 -> repo.getAuthors()
                else -> repo.getGenres()
            }
            false // Onboarding is not yet complete.
        } else {
            repo.submitSelections()
            true // Onboarding is complete.
        }
    }
}
