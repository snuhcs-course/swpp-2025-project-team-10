package com.example.librarytogether.feature.search

import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentSearchBinding
import com.example.librarytogether.feature.search.data.SearchItem
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class SearchFragment : Fragment(R.layout.fragment_search) {

    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SearchViewModel by viewModels()

    private val adapter: SearchResultAdapter by lazy {
        SearchResultAdapter(onClick = ::onClickResult)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentSearchBinding.bind(view)

        setupRecyclerView()
        setupSearchUi()
        observeViewModel()
    }

    private fun setupRecyclerView() = with(binding) {
        rvSearchResults.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = this@SearchFragment.adapter
            setHasFixedSize(true)
        }
    }

    private fun setupSearchUi() = with(binding) {
        searchView.setupWithSearchBar(searchBar)

        searchView.editText.setOnEditorActionListener { v, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                viewModel.search(v.text.toString())
                true
            } else false
        }
    }

    private fun observeViewModel() {
        viewModel.results.observe(viewLifecycleOwner) { list ->
            adapter.submitList(list)
        }
        viewModel.error.observe(viewLifecycleOwner) { err ->
            err?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                viewModel.onErrorShown()
            }
        }
        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
        }
    }

    private fun onClickResult(item: SearchItem) {
        // TODO: 상세/교환 화면으로 이동
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
