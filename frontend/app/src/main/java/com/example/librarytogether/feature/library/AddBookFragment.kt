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
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentAddBookBinding
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.PostBook
import com.example.librarytogether.util.loadCover
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import reactivecircus.flowbinding.android.widget.textChanges
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach
import kotlin.io.path.Path
import android.util.Log
@AndroidEntryPoint
class AddBookFragment : Fragment(R.layout.fragment_add_book) {

    private var _binding: FragmentAddBookBinding? = null
    private val binding get() = _binding!!

    private val viewModel: LibraryViewModel by activityViewModels()

    private var selectedPublicationId: String? = null

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
        btnSaveBook.text = "내 책장에 저장"
        switchBarterAvailable.visibility = View.VISIBLE
        switchBarterAvailable.isEnabled = true
    }

    private fun setupClickListeners() {
        binding.btnSaveBook.setOnClickListener {
                saveToBookshelf()
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
            Snackbar.make(requireView(), "책 제목과 저자는 필수입니다.", Snackbar.LENGTH_SHORT).show()
            return
        }

        val publicationId = selectedPublicationId

        val postBook = if (publicationId.isNullOrBlank()) {
            // No existing publication - send fields to create new publication
            Log.d("BookDebug", "Creating new publication for: $title")
            PostBook(
                publication = null,
                book_title = title,
                book_authors = authors.split(",").map { it.trim() }, // Convert string to list
                book_publisher = publisher.takeIf { it.isNotBlank() },
                book_isbn_13 = isbn.takeIf { it.isNotBlank() },
                is_for_barter = isBarterAvailable
            )
        } else {
            // Existing publication - just send publication ID
            Log.d("BookDebug", "Using existing publication: $publicationId")
            PostBook(
                publication = publicationId,
                is_for_barter = isBarterAvailable
            )
        }
        Log.d("BookDebug", "PostBook data: $postBook")
        viewModel.addNewBook(postBook)
    }

    private fun setupSearchHandler() {
        binding.toolbarAddBook.setNavigationOnClickListener {
            findNavController().popBackStack()
        }
        binding.toolbarAddBook.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.action_search -> {
                    binding.searchView.show()
                    true
                }
                else -> false
            }
        }

        binding.rvSearchResults.adapter = searchAdapter
        binding.rvSearchResults.layoutManager = LinearLayoutManager(requireContext())


        val edit = binding.searchView.editText

        edit.setOnEditorActionListener { v, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                val query = v.text.toString().trim()
                if (query.isNotEmpty()) {
                    viewModel.searchBook(query)
                }
                true
            } else {
                false
            }
        }

        // 2) textChanges + debounce 로 실시간 검색
        viewLifecycleOwner.lifecycleScope.launch {
            edit.textChanges()
                .debounce(300)
                .map { it.toString().trim() }
                .distinctUntilChanged()
                .onEach { query ->
                    val isEmpty = query.isEmpty()

                    if (isEmpty) {
                        viewModel.clearSearch()
                    }
                }
                .filter { it.isNotEmpty() }
                .collectLatest { query ->
                    viewModel.searchBook(query)
                }
        }

        binding.searchView.addTransitionListener { _, _, newState ->
            if (newState == SearchView.TransitionState.HIDDEN) {
                edit.text = null
                viewModel.clearSearch()
            }
        }
    }

    private fun onBookSearchResultClicked(book: Book) {
        selectedPublicationId = book.publicationId

        binding.etTitle.setText(book.title)
        binding.etAuthor.setText(book.authors?.joinToString(", ") ?: "")
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
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
