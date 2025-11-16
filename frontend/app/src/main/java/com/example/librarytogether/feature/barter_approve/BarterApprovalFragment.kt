package com.example.librarytogether.feature.barterapproval

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentBarterApprovalBinding
import com.example.librarytogether.feature.barterapproval.BarterApprovalViewModel.UiState
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.BookAdapter
import com.example.librarytogether.feature.library.BookClicks
import com.example.librarytogether.feature.library.BookListMode
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.util.loadAvatar
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class BarterApprovalFragment : Fragment(R.layout.fragment_barter_approval) {

    private var _binding: FragmentBarterApprovalBinding? = null
    private val binding get() = _binding!!

    private val viewModel: BarterApprovalViewModel by viewModels()
    private val args: BarterApprovalFragmentArgs by navArgs()
    private val requestId by lazy { args.requestId }

    private lateinit var adapter: BookAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentBarterApprovalBinding.bind(view)

        setupToolbar()
        setupRecycler()
        setupButtons()
        observeViewModel()
        observeSelectedBook()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            findNavController().popBackStack()
        }
    }

    private fun setupRecycler() {
        adapter = BookAdapter(
            mode = BookListMode.ROW,
            clicks = BookClicks(
                // 상세보기는 btnMore 로
                onClickItem = { },
                onClickMore = { book, _ -> openBookDetail(book) },
                onSelect = { book -> viewModel.toggleSelectedBook(book) }
            )
        )
        binding.rvBooks.adapter = adapter
    }

    private fun openBookDetail(book: Book) {
        val action =
            BarterApprovalFragmentDirections
                .actionBarterApprovalFragmentToBookDetailFragment(
                    bookId = book.id,
                    source = EntrySource.EXPLORE
                )
        findNavController().navigate(action)
    }

    @SuppressLint("StringFormatInvalid")
    private fun setupButtons() {
        binding.btnReject.setOnClickListener {
            val selected = viewModel.selectedBook.value

            if (selected == null) {
                viewModel.rejectRequest {
                    Toast.makeText(
                        requireContext(),
                        getString(R.string.msg_barter_request_rejected),
                        Toast.LENGTH_SHORT
                    ).show()
                    findNavController().popBackStack()
                }
            } else {
                viewModel.acceptBook(selected)
                Toast.makeText(
                    requireContext(),
                    getString(R.string.msg_barter_book_accepted, selected.title),
                    Toast.LENGTH_SHORT
                ).show()
                findNavController().popBackStack()
            }
        }
    }

    private fun observeSelectedBook() {
        viewModel.selectedBook.observe(viewLifecycleOwner) { selected ->
            binding.btnReject.text =
                if (selected == null) "거절" else "수락"
        }
    }

    private fun observeViewModel() {
        viewModel.state.observe(viewLifecycleOwner) { st ->
            when (st) {
                is UiState.Loading -> renderLoading()
                is UiState.Error -> renderError(st.message)
                is UiState.Data -> renderData(st)
            }
        }
    }

    private fun renderLoading() = with(binding) {
        progress.isVisible = true
        tvError.isVisible = false
        contentGroup.isVisible = false
    }

    private fun renderError(msg: String) = with(binding) {
        progress.isVisible = false
        tvError.isVisible = true
        tvError.text = msg
        contentGroup.isVisible = false
    }

    private fun renderData(state: UiState.Data) = with(binding) {
        progress.isVisible = false
        tvError.isVisible = false
        contentGroup.isVisible = true

        val detail = state.detail

        tvRequesterName.text = detail.requesterName
        tvCreatedAt.text = detail.createdAt
        tvMessage.text = detail.message.orEmpty().joinToString("\n")
        imgAvatar.loadAvatar(detail.requesterAvatarUrl)

        adapter.submitList(detail.books)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
