package com.example.librarytogether.feature.onboarding

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.map
import com.example.librarytogether.feature.onboarding.data.LabelId
import com.example.librarytogether.feature.onboarding.data.OnboardingRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject
import androidx.lifecycle.viewModelScope

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val repo: OnboardingRepository
) : ViewModel() {

    private val _currentStep = MutableLiveData(0)
    val currentStep: LiveData<Int> = _currentStep

    private val _displayItems = MutableLiveData<List<ChipSelectableAdapter.Item>>(emptyList())
    val displayItems: LiveData<List<ChipSelectableAdapter.Item>> = _displayItems

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // 온보딩 완료 시 Activity 전환을 위한 이벤트
    private val _onboardingFinished = MutableLiveData<Boolean>(false)
    val onboardingFinished: LiveData<Boolean> = _onboardingFinished


    // 현재 단계에서 선택된 아이템 ID들
    private val _selected = MutableLiveData<Set<String>>(emptySet())
    val selectedIds: LiveData<List<String>> = _selected.map { it.toList() }

    val canProceed: LiveData<Boolean> = _selected.map { it.size >= 3 }

    fun loadInitial() {
        loadItemsForStep(0)
    }

    private fun loadItemsForStep(step: Int) {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val items = when (step) {
                    0 -> repo.getBooks()
                    1 -> repo.getAuthors()
                    2 -> repo.getGenres()
                    else -> emptyList()
                }
                _displayItems.value = items.map { ChipSelectableAdapter.Item(it.id, it.label) }
            } catch (e: Exception) {
                _error.value = "데이터를 불러오는 데 실패했습니다."
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun toggleSelection(id: String, isSelected: Boolean) {
        val currentSet = _selected.value ?: emptySet()
        val newSet = if (isSelected) currentSet + id else currentSet - id
        _selected.value = newSet
    }

    suspend fun nextStep(): Boolean {
        val step = _currentStep.value ?: 0
        val selectedIds = _selected.value?.toList() ?: emptyList()
        repo.saveSelection(step, selectedIds)

        if (step < 2) {
            // 다음 단계로 이동
            val nextStep = step + 1
            _currentStep.value = nextStep
            _selected.value = emptySet()
            loadItemsForStep(nextStep)
        } else {
            // 마지막 단계, 서버에 제출
            submitOnboarding()
        }
    }

    private fun submitOnboarding() {
        _isLoading.value = true
        viewModelScope.launch {
            val success = try { repo.submitSelections() } catch (e: Exception) { false }
            if (success) {
                _onboardingFinished.value = true
            } else {
                _error.value = "선택 항목 제출에 실패했습니다."
            }
            _isLoading.value = false
        }
    }
}
