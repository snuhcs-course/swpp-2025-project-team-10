package com.example.librarytogether.feature.explore

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentExploreBinding
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.BookAdapter
import com.example.librarytogether.feature.library.BookClicks
import com.example.librarytogether.feature.library.BookListMode
import com.example.librarytogether.feature.library.data.Book
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ExploreFragment : Fragment(R.layout.fragment_explore) {

    private var _binding: FragmentExploreBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ExploreViewModel by viewModels()

    private val adapter by lazy {
        BookAdapter(
            mode = BookListMode.ROW,
            clicks = BookClicks(
                onClickItem = { book ->
                    val id = book.id
                    val dir = BookDetailFragmentDirections.actionGlobalBookDetail(
                        bookId = id,
                        source = EntrySource.EXPLORE
                    )
                    findNavController().navigate(dir)
                }
            )
        )
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentExploreBinding.bind(view)

        setupRecycler()
        observeViewModel()
        viewModel.loadRecommendations()
    }

    private fun setupRecycler() {
        binding.listRecommendations.adapter = adapter
        binding.listRecommendations.itemAnimator = null
    }


    private fun observeViewModel() = with(binding) {
        viewModel.state.observe(viewLifecycleOwner) { st ->
            when (st) {
                is ExploreUi.Loading -> renderLoading(true)
                is ExploreUi.Error -> renderError(st.message)
                is ExploreUi.Data -> renderData(st.items)
                is ExploreUi.Empty -> renderEmpty()
            }
        }
    }

    private fun renderLoading(loading: Boolean) {
        binding.progress.isVisible = loading
        binding.listRecommendations.isVisible = !loading
        binding.tvEmpty.isVisible = false
        binding.tvError.isVisible = false
    }

    private fun renderError(msg: String) {
        binding.progress.isVisible = false
        binding.listRecommendations.isVisible = false
        binding.tvEmpty.isVisible = false
        binding.tvError.isVisible = true
        binding.tvError.text = msg
    }

    private fun renderEmpty() {
        binding.progress.isVisible = false
        binding.listRecommendations.isVisible = false
        binding.tvError.isVisible = false
        binding.tvEmpty.isVisible = true
    }

    private fun renderData(items: List<Book>) {
        binding.progress.isVisible = false
        binding.tvEmpty.isVisible = items.isEmpty()
        binding.tvError.isVisible = false
        binding.listRecommendations.isVisible = items.isNotEmpty()
        adapter.submitList(items)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
