package com.example.librarytogether.feature.search

import android.os.Bundle
import android.view.ContextThemeWrapper
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentSearchBinding
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.home.HomeViewModel
import com.example.librarytogether.feature.search.data.SearchItem
import com.google.android.material.chip.Chip
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import reactivecircus.flowbinding.android.widget.textChanges

@AndroidEntryPoint
class SearchFragment : Fragment(R.layout.fragment_search) {

    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!

    private val searchViewModel: SearchViewModel by viewModels()
    private val searchSharedViewModel: SearchSharedViewModel by activityViewModels()
    private val homeViewModel: HomeViewModel by activityViewModels()

    private val searchResultAdapter: SearchResultAdapter by lazy {
        SearchResultAdapter(onClick = ::onClickResult)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentSearchBinding.bind(view)

        searchSharedViewModel.pendingQuery.observe(viewLifecycleOwner) { query ->
            if (!query.isNullOrBlank()) {
                binding.etSearch.setText(query)
                binding.etSearch.setSelection(query.length)
                searchViewModel.search(query)
                searchSharedViewModel.clearQuery()
            }
        }

        setupRecyclerView()
        observeViewModel()
        setupSearchEditText()
    }

    private fun setupRecyclerView() = with(binding) {
        rvSearchResults.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = this@SearchFragment.searchResultAdapter
            setHasFixedSize(true)
        }
    }

    private fun setupSearchEditText() = with(binding) {
        val edit = etSearch

        edit.setOnEditorActionListener { v, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                val query = v.text.toString().trim()
                if (query.isNotEmpty()) {
                    searchViewModel.search(query)
                }
                true
            } else {
                false
            }
        }

        lifecycleScope.launch {
            edit.textChanges()
                .debounce(300)
                .map { it.toString().trim() }
                .distinctUntilChanged()
                .onEach { query ->
                    val showRecommend = query.isEmpty()
                    tvRecommendedTitle.isVisible =
                        showRecommend && chipGroupRecommended.childCount > 0
                    chipGroupRecommended.isVisible =
                        showRecommend && chipGroupRecommended.childCount > 0

                    if (showRecommend) {
                        searchViewModel.clearSearch()
                    }
                }
                .filter { it.isNotEmpty() }
                .collectLatest { query ->
                    searchViewModel.search(query)
                }
        }
    }

    private fun observeViewModel() = with(binding) {
        searchViewModel.results.observe(viewLifecycleOwner) { list ->
            searchResultAdapter.submitList(list)
            rvSearchResults.isVisible = list.isNotEmpty()
            val hasQuery = etSearch.text?.isNotBlank() == true
            tvSearchEmpty.isVisible = list.isEmpty() && hasQuery
        }

        searchViewModel.error.observe(viewLifecycleOwner) { err ->
            err?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                searchViewModel.onErrorShown()
            }
        }

        homeViewModel.posts.observe(viewLifecycleOwner) { posts ->
            val titles = posts
                .mapNotNull { post -> post.bookTitle }  // null 제외
                .map { it.trim() }
                .filter { it.isNotEmpty() }              // 공백만 있는 제목 제외
                .distinct()
                .shuffled()
                .take(6)

            renderRecommended(titles)

            val queryEmpty = etSearch.text?.isBlank() == true
            tvRecommendedTitle.isVisible = queryEmpty && titles.isNotEmpty()
            chipGroupRecommended.isVisible = queryEmpty && titles.isNotEmpty()
        }

        searchViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
        }
    }

    private fun renderRecommended(titles: List<String>) {
        val group = binding.chipGroupRecommended
        group.removeAllViews()

        titles.forEach { title ->
            val chip = Chip(
                ContextThemeWrapper(requireContext(), R.style.TextOnlyChip),
                null,
                0
            ).apply {
                text = title
                isCheckable = false
                isClickable = true

                setOnClickListener {
                    binding.etSearch.setText(title)
                    binding.etSearch.setSelection(title.length)
                    searchViewModel.search(title)
                }
            }
            group.addView(chip)
        }
    }

    private fun onClickResult(item: SearchItem) {
        val dir = BookDetailFragmentDirections
            .actionGlobalBookDetail(
                bookId = item.id,
                source = EntrySource.SEARCH
            )
        findNavController().navigate(dir)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
