package com.example.librarytogether.feature.onboarding

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentOnboardingBinding
import com.example.librarytogether.feature.main.MainActivity
import com.google.android.flexbox.FlexWrap
import com.google.android.flexbox.FlexboxLayoutManager
import com.google.android.flexbox.JustifyContent
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class OnboardingFragment : Fragment(R.layout.fragment_onboarding) {

    private var _binding: FragmentOnboardingBinding? = null
    private val binding get() = _binding!!

    private val viewModel: OnboardingViewModel by viewModels()

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
            viewLifecycleOwner.lifecycleScope.launch {
                val isFinished = viewModel.nextStep()
                if (isFinished) navigateToMain()
            }
        }

        viewModel.loadInitial()
    }

    private fun setupRecyclerView() {
        binding.rvChips.apply {
            layoutManager = FlexboxLayoutManager(requireContext()).apply {
                flexWrap = FlexWrap.WRAP
                justifyContent = JustifyContent.FLEX_START
            }
            adapter = chipAdapter
        }
    }

    private fun observeViewModel() {
        viewModel.displayItems.observe(viewLifecycleOwner) { list ->
            val items = list.map { ChipSelectableAdapter.Item(it.id, it.name) }
            chipAdapter.submitList(items)
        }

        viewModel.selectedIds.observe(viewLifecycleOwner) { selectedIds ->
            chipAdapter.updateSelection(selectedIds.toSet())
        }

        viewModel.currentStep.observe(viewLifecycleOwner) { step ->
            binding.tvTitle.text = when (step) {
                0 -> getString(R.string.onboarding_title_books)
                1 -> getString(R.string.onboarding_title_authors)
                else -> getString(R.string.onboarding_title_genres)
            }
            binding.btnNext.text =
                if (step < 2) getString(R.string.next) else getString(R.string.done)
        }

        viewModel.canProceed.observe(viewLifecycleOwner) { canProceed ->
            binding.btnNext.isEnabled = canProceed
        }
    }

    private fun navigateToMain() {
        if (!isAdded) return

        val intent = Intent(requireContext(), MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
    }

    override fun onDestroyView() {
        binding.rvChips.adapter = null
        _binding = null
        super.onDestroyView()
    }
}
