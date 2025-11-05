package com.example.librarytogether.feature.explore

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentExploreBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ExploreFragment : Fragment(R.layout.fragment_explore) {

    private var _binding: FragmentExploreBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ExploreViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentExploreBinding.bind(view)

        setupUi()
        observeViewModel()
    }

    private fun setupUi() = with(binding) {
    }

    private fun observeViewModel() = with(binding) {
        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            progress.isVisible = loading
            contentContainer.isVisible = !loading
        }
        viewModel.error.observe(viewLifecycleOwner) { msg ->
            msg?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                viewModel.onErrorShown()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
