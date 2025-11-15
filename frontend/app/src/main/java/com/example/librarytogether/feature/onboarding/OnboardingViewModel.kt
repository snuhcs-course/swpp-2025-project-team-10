package com.example.librarytogether.feature.onboarding

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.map
import androidx.lifecycle.viewModelScope
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
        val currentSet = _selected.value ?: emptySet()
        val newSet = if (isSelected) currentSet + id else currentSet - id
        _selected.value = newSet
    }

    fun loadInitial() {
        viewModelScope.launch {
            _displayItems.value = repo.getBooks()
        }
    }

    suspend fun nextStep(): Boolean {
        val step = _currentStep.value ?: 0
        val selectedIds = _selected.value?.toList() ?: emptyList()

        repo.saveSelection(step, selectedIds)

        return if (step < 2) {
            val next = step + 1
            _selected.value = emptySet()
            _currentStep.value = next

            _displayItems.value = when (next) {
                1 -> repo.getAuthors()
                else -> repo.getGenres()
            }
            false
        } else {
            repo.submitSelections()
            true
        }
    }
}
