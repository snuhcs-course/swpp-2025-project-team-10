package com.example.librarytogether.feature.barterapproval

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.bumptech.glide.Glide
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentBarterApprovalBinding
import com.example.librarytogether.feature.barterapproval.BarterApprovalViewModel.UiState
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
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
    private var currentDetail: BarterApprovalDetail? = null

    private lateinit var adapter: BookAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentBarterApprovalBinding.bind(view)
        val binding = binding

        setupToolbar()
        setupRecycler()
        setupRejectButton()
        observeViewModel()
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
                onClickItem = { book -> openBookDetail(book) },
                onClickMore = { book, _ -> acceptBook(book) }
            )
        )
        binding.rvBooks.adapter = adapter
    }

    private fun openBookDetail(book: Book) {
        val detail = currentDetail ?: return
        val index = detail.books.indexOfFirst { it.id == book.id }
        val messageForThisBook: String? =
            if (index in detail.message.indices) detail.message[index] else null

        val action =
            BarterApprovalFragmentDirections
                .actionBarterApprovalFragmentToBookDetailFragment(
                    bookId = book.id,
                    source = EntrySource.EXPLORE,
                    barterMessage = messageForThisBook
                )
        findNavController().navigate(action)
    }

    private fun acceptBook(book: Book) {
        viewModel.acceptBook(book)
    }

    private fun setupRejectButton() {
        binding.btnReject.setOnClickListener {
            viewModel.rejectRequest {
                findNavController().popBackStack()
            }
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
        currentDetail = detail

        tvRequesterName.text = detail.requesterName
        tvCreatedAt.text = detail.createdAt
        tvMessage.text = getString(R.string.barter_message_to_user, detail.requesterName)
        binding.imgAvatar.loadAvatar(detail.requesterAvatarUrl)

        adapter.submitList(detail.books)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
