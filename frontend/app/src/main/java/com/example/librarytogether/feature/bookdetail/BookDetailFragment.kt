package com.example.librarytogether.feature.bookdetail

import android.content.res.ColorStateList
import android.os.Bundle
import android.view.View
import androidx.annotation.ColorRes
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentBookDetailBinding
import com.example.librarytogether.feature.bookdetail.BookDetailViewModel.UiState
import com.example.librarytogether.feature.bookdetail.data.BookDetail
import com.example.librarytogether.feature.library.LibraryViewModel
import com.example.librarytogether.util.loadCover
import dagger.hilt.android.AndroidEntryPoint

enum class EntrySource {SEARCH, WISHLIST, EXPLORE, BOOKSHELF, BARTERAPPROVAL}

@AndroidEntryPoint
class BookDetailFragment : Fragment(R.layout.fragment_book_detail) {

    private var _binding: FragmentBookDetailBinding? = null
    private val binding get() = _binding!!
    private val viewModel: BookDetailViewModel by viewModels()
    private val libraryViewModel: LibraryViewModel by activityViewModels()
    private val args: BookDetailFragmentArgs by navArgs()
    private val bookId by lazy { args.bookId }
    private val source get() = args.source


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentBookDetailBinding.bind(view)

        setupToolbar()
        setupClicks()
        observeViewModel()

        if (savedInstanceState == null) {
            viewModel.load()
        }
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            findNavController().popBackStack()
        }
    }

    private fun setupClicks() {
        binding.btnPrimary.setOnClickListener {
            val state = viewModel.state.value as? UiState.Data ?: return@setOnClickListener
            when (source) {
                EntrySource.BARTERAPPROVAL -> {
                }
                else -> {
                }
            }
        }

        binding.fabWishlist.setOnClickListener {
            libraryViewModel.toggleWishlistById(bookId)
        }
    }

    private fun observeViewModel() {
        viewModel.state.observe(viewLifecycleOwner) { st ->
            when (st) {
                is UiState.Loading -> renderLoading(true)
                is UiState.Error -> renderError(st.message)
                is UiState.Data -> renderData(st)
            }
        }

        libraryViewModel.isWishlisted(bookId).observe(viewLifecycleOwner) { isWish ->
            val icon = if (isWish) R.drawable.filled_like_icon else R.drawable.favorite_icon
            binding.fabWishlist.setImageResource(icon)
            binding.fabWishlist.contentDescription =
                if (isWish) getString(R.string.status_wishlist)
                else getString(R.string.action_add_wishlist)
        }
    }

    private fun renderLoading(loading: Boolean) {
        binding.progress.isVisible = loading
        binding.tvError.isVisible = false
        binding.btnPrimary.isEnabled = !loading
    }

    private fun renderError(msg: String) {
        binding.progress.isVisible = false
        binding.tvError.isVisible = true
        binding.tvError.text = msg
        binding.btnPrimary.isEnabled = false
    }

    private fun renderData(state: UiState.Data) {
        binding.progress.isVisible = false
        binding.tvError.isVisible = false

        val book = state.book
        binding.tvTitle.text = book.title
        binding.tvAuthor.text = book.authors?.joinToString(", ") ?: ""
        binding.tvPublisher.text = book.publisher.orEmpty()
        binding.tvIsbn.text = book.isbn.orEmpty()
        binding.tvDescription.apply {
            isVisible = !book.description.isNullOrBlank()
            text = book.description ?: ""
        }
        binding.imgCover.loadCover(book.cover_image)

        renderPrimaryButton(source, book)
    }

    private fun renderPrimaryButton(source: EntrySource, b: BookDetail) {
        when (source) {
            EntrySource.BARTERAPPROVAL -> {
                binding.btnPrimary.isEnabled = true
                binding.btnPrimary.text = getString(R.string.action_barter_approve)
                setBtnBg(R.color.black)
            }
            else -> {
                binding.btnPrimary.isEnabled = b.is_for_barter
                binding.btnPrimary.text = if (b.is_for_barter)
                    getString(R.string.action_request_barter)
                else
                    getString(R.string.unavailable_for_trade)
                setBtnBg(if (b.is_for_barter) R.color.black else R.color.grey)
            }
        }
    }

    private fun setBtnBg(@ColorRes colorRes: Int) {
        val c = ContextCompat.getColor(requireContext(), colorRes)
        binding.btnPrimary.backgroundTintList = ColorStateList.valueOf(c)
    }



    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
