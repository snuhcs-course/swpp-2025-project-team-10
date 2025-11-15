package com.example.librarytogether.feature.library

import android.content.Context
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.Toast
import com.google.android.material.search.SearchView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentAddBookBinding
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.PostBook
import com.example.librarytogether.util.loadCover
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class AddBookFragment : Fragment(R.layout.fragment_add_book) {

    private var _binding: FragmentAddBookBinding? = null
    private val binding get() = _binding!!

    private val viewModel: LibraryViewModel by activityViewModels()

    private val args by navArgs<AddBookFragmentArgs>()

    private val searchAdapter by lazy {
        SearchBookAdapter(::onBookSearchResultClicked) // 클릭 시 onBookSearchResultClicked 함수 호출
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentAddBookBinding.bind(view)
        binding.imgCover.loadCover(null)

        setupClickListeners()
        setupSearchHandler()
        setupUiByMode()
        observeViewModel()
    }

    private fun setupUiByMode() = with(binding) {
        when (args.mode) {
            AddBookMode.BOOKSHELF -> {
                btnSaveBook.text = "내 책장에 저장"
                switchBarterAvailable.visibility = View.VISIBLE
                switchBarterAvailable.isEnabled = true
            }
            AddBookMode.WISHLIST -> {
                btnSaveBook.text = "위시리스트에 추가"
                switchBarterAvailable.isChecked = false
                switchBarterAvailable.visibility = View.GONE
            }
        }
    }

    private fun setupClickListeners() {
        binding.btnSaveBook.setOnClickListener {
            when (args.mode) {
                AddBookMode.BOOKSHELF -> saveToBookshelf()
                AddBookMode.WISHLIST -> addToWishlist()
            }
        }

        binding.fabEditCover.setOnClickListener {
            // TODO: 갤러리/카메라 열어서 이미지 선택
        }
    }

    private fun saveToBookshelf() {
        val title = binding.etTitle.text.toString()
        val authors = binding.etAuthor.text.toString()
        val publisher = binding.etPublisher.text.toString()
        val isbn = binding.etIsbn.text.toString()
        val isBarterAvailable = binding.switchBarterAvailable.isChecked

        if (title.isBlank() || authors.isBlank()) {
            Toast.makeText(requireContext(), "책 제목과 저자는 필수입니다.", Toast.LENGTH_SHORT).show()
            return
        }

        val postBook = PostBook(
            title = title,
            authors = authors,
            publisher = publisher.takeIf { it.isNotBlank() },
            isbn = isbn.takeIf { it.isNotBlank() },
            is_for_barter = isBarterAvailable,
            //coverUrl =
        )
        viewModel.addNewBook(postBook)
    }

    private fun addToWishlist() {
        val title = binding.etTitle.text.toString()
        val authors = binding.etAuthor.text.toString()
        val publisher = binding.etPublisher.text.toString()
        val isbn = binding.etIsbn.text.toString()

        if (title.isBlank() || authors.isBlank()) {
            Toast.makeText(requireContext(), "책 제목과 저자는 필수입니다.", Toast.LENGTH_SHORT).show()
            return
        }

        val postBook = Book(
            id = "",
            title = title,
            authors = authors,
            publisher = publisher.takeIf { it.isNotBlank() },
            isbn = isbn.takeIf { it.isNotBlank() },
            cover_image = ""
        )

        viewModel.addToWishlist(postBook)

        findNavController().previousBackStackEntry
            ?.savedStateHandle
            ?.set("switch_tab", "PROFILE")

        findNavController().popBackStack()
    }

    private fun setupSearchHandler() {
        binding.searchView.setupWithSearchBar(binding.searchBar)

        binding.rvSearchResults.adapter = searchAdapter
        binding.rvSearchResults.layoutManager = LinearLayoutManager(requireContext())


        binding.searchView
            .getEditText()
            .setOnEditorActionListener { v, actionId, event ->
                if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                    val query = binding.searchView.text.toString()
                    if (!query.isNullOrBlank()) {
                        viewModel.searchBook(query)
                        hideKeyboard()
                    }
                    return@setOnEditorActionListener true
                }
                return@setOnEditorActionListener false
            }
        binding.searchView.addTransitionListener { _, _, newState ->
            if (newState == SearchView.TransitionState.HIDDEN || newState == SearchView.TransitionState.HIDING) {
                viewModel.clearSearch()
            }
        }
    }

    private fun onBookSearchResultClicked(book: Book) {
        binding.etTitle.setText(book.title)
        binding.etAuthor.setText(book.authors)
        binding.etPublisher.setText(book.publisher)
        binding.etIsbn.setText(book.isbn)
        binding.imgCover.loadCover(book.cover_image)

        binding.searchView.hide()
    }

    private fun observeViewModel() {
        viewModel.navigateToLibrary.observe(viewLifecycleOwner) { navigate ->
            if (navigate) {
                findNavController().popBackStack()
                viewModel.onBookAddedNavigationComplete()
            }
        }
        viewModel.searchResults.observe(viewLifecycleOwner) { results ->
            searchAdapter.submitList(results)
            binding.rvSearchResults.visibility = if (results.isNotEmpty()) View.VISIBLE else View.GONE
        }
    }

    private fun hideKeyboard() {
        val imm = requireContext().getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        imm.hideSoftInputFromWindow(binding.searchView.windowToken, 0)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
