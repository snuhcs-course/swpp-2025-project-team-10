package com.example.librarytogether.feature.onboarding

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentOnboardingBinding
// Unused import, can be removed: import com.example.librarytogether.feature.onboarding.ChipSelectableAdapter
import com.example.librarytogether.feature.main.MainActivity
import com.google.android.flexbox.FlexWrap
import com.google.android.flexbox.FlexboxLayoutManager
import com.google.android.flexbox.JustifyContent
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class OnboardingFragment : Fragment(R.layout.fragment_onboarding) {

    private var _binding: FragmentOnboardingBinding? = null
    private val binding get() = _binding!! // This is generally safe in Fragments between onViewCreated and onDestroyView

    private val viewModel: OnboardingViewModel by viewModels()

    // Initialize adapter lazily to ensure context is available
    private val chipAdapter: ChipSelectableAdapter by lazy {
        ChipSelectableAdapter { id, isSelected ->
            viewModel.toggleSelection(id, isSelected)
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentOnboardingBinding.bind(view)

        setupRecyclerView()
        observeViewModel()

        binding.btnNext.setOnClickListener {
            // It's safer to launch the coroutine within the ViewModel's scope if it's a long-running task,
            // but for a quick navigation action, lifecycleScope is fine.
            viewLifecycleOwner.lifecycleScope.launch {
                val isFinished = viewModel.nextStep()
                if (isFinished) {
                    navigateToMain()
                }
            }
        }

        // Load initial data after observers are set up
        viewModel.loadInitial()
    }

    private fun setupRecyclerView() {
        binding.rvChips.apply {
            // Use a FlexboxLayoutManager for chip-like layouts
            layoutManager = FlexboxLayoutManager(requireContext()).apply {
                flexWrap = FlexWrap.WRAP
                justifyContent = JustifyContent.FLEX_START
            }
            adapter = chipAdapter
            // Optional: Add item animator for smoother UI updates
            // itemAnimator = DefaultItemAnimator()
        }
    }

    private fun observeViewModel() {
        // Observer for the list of items to display
        viewModel.displayItems.observe(viewLifecycleOwner) { list ->
            val items = list.map { ChipSelectableAdapter.Item(it.id, it.name) }
            // Submit the new list of items to the adapter
            chipAdapter.submitList(items)
        }

        // Observer for the set of currently selected IDs
        viewModel.selectedIds.observe(viewLifecycleOwner) { selectedIds ->
            // Pass the updated set of selected IDs to the adapter to re-render selections
            chipAdapter.updateSelection(selectedIds.toSet())
        }

        // Observer for the current step to update UI text
        viewModel.currentStep.observe(viewLifecycleOwner) { step ->
            binding.tvTitle.text = when (step) {
                0 -> getString(R.string.onboarding_title_books) // Use string resources
                1 -> getString(R.string.onboarding_title_authors)
                else -> getString(R.string.onboarding_title_genres)
            }
            binding.btnNext.text = if (step < 2) getString(R.string.next) else getString(R.string.done)
        }


        // Observer to enable/disable the "Next" button
        viewModel.canProceed.observe(viewLifecycleOwner) { canProceed ->
            binding.btnNext.isEnabled = canProceed
        }
    }

    private fun navigateToMain() {
        // Defensive check to prevent crash if activity is not available
        if (!isAdded) return

        val intent = Intent(requireContext(), MainActivity::class.java).apply {
            // Clear the task stack so the user cannot navigate back to onboarding
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
    }

    override fun onDestroyView() {
        // To avoid memory leaks, nullify the binding and remove the adapter from the RecyclerView
        binding.rvChips.adapter = null
        _binding = null
        super.onDestroyView()
    }
}
