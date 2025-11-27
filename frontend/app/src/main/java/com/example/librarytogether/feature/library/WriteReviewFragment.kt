package com.example.librarytogether.feature.library

import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentWriteReviewBinding
import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.PostReview
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import reactivecircus.flowbinding.android.widget.textChanges
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.Job
import com.google.android.material.search.SearchView

@AndroidEntryPoint
class WriteReviewFragment : Fragment(R.layout.fragment_write_review) {

    private val parentViewModel: LibraryViewModel by activityViewModels()

    private val selectedUrls = mutableListOf<Uri>()
    private lateinit var photoAdapter: PhotoAdapter

    private lateinit var bookSearchAdapter: SearchBookAdapter
    private var allMyBooks: List<Book> = emptyList()
    private var searchJob: Job? = null

    private var selectedBookId: String? = null

    private var _binding: FragmentWriteReviewBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentWriteReviewBinding.bind(view)

        setupToolbar()
        setupRecyclerView()
        observeViewModel()
        setupSearch()
        setupListeners()

    }

    private fun setupToolbar() = with(binding) {
        toolbarWriteReview.setNavigationOnClickListener {
            findNavController().popBackStack()
        }
        toolbarWriteReview.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.action_search -> {
                    searchView.show()
                    true
                }
                else -> false
            }
        }
    }

    private fun setupRecyclerView() = with(binding) {
        photoAdapter = PhotoAdapter(
            onRemove = { uri ->
                selectedUrls.remove(uri)
                photoAdapter.submitList(selectedUrls.toList())
                togglePhotoViews()
            }
        )
        rvPhotos.apply {
            layoutManager = LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
            adapter = photoAdapter
            setHasFixedSize(true)
        }

        bookSearchAdapter = SearchBookAdapter { book ->
            selectedBookId = book.id

            if (etBookTitle.text.isNullOrBlank()) {
                etBookTitle.setText(book.title)
            }
            if (etAuthor.text.isNullOrBlank()) {
                etAuthor.setText(book.authors?.joinToString(", ") ?: "")
            }
            if (etPublisher.text.isNullOrBlank()) {
                etPublisher.setText(book.publisher ?: "")
            }
            if (etIsbn.text.isNullOrBlank()) {
                etIsbn.setText(book.isbn ?: "")
            }

            searchView.hide()
        }

        rvBookSearchResults.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = bookSearchAdapter
            setHasFixedSize(true)
        }
    }

    private fun observeViewModel() {
        parentViewModel.myBooks.observe(viewLifecycleOwner) { books ->
            allMyBooks = books ?: emptyList()
        }
    }

    private fun setupSearch() = with(binding) {
        val edit = searchView.editText

        edit.setOnEditorActionListener { v, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                val query = v.text.toString().trim()
                if (query.isNotEmpty()) {
                    applyBookFilter(query)
                } else {
                    bookSearchAdapter.submitList(emptyList())
                }
                true
            } else {
                false
            }
        }

        // 2) textChanges + debounce로 실시간 검색
        viewLifecycleOwner.lifecycleScope.launch {
            searchJob?.cancel()
            searchJob = launch {
                edit.textChanges()
                    .debounce(300)
                    .map { it.toString().trim() }
                    .distinctUntilChanged()
                    .collectLatest { query ->
                        if (query.isEmpty()) {
                            // 검색어가 없으면 내 전체 책을 보여주거나, 비워두고 싶으면 빈 리스트
                            bookSearchAdapter.submitList(allMyBooks)
                        } else {
                            applyBookFilter(query)
                        }
                    }
            }
        }

        // 3) SearchView 열릴 때 / 닫힐 때 처리
        searchView.addTransitionListener { _: SearchView, _: SearchView.TransitionState, newState: SearchView.TransitionState ->
            when (newState) {
                SearchView.TransitionState.SHOWN -> {
                    // 처음 열릴 때: 전체 책장 책을 보여줌
                    bookSearchAdapter.submitList(allMyBooks)
                }
                SearchView.TransitionState.HIDDEN -> {
                    // 닫힐 때: 검색어/결과 정리
                    edit.text = null
                    bookSearchAdapter.submitList(emptyList())
                }
                else -> Unit
            }
        }
    }

    private fun applyBookFilter(query: String) {
        val q = query.trim()
        val filtered = allMyBooks.filter { book ->
            val matchTitle = book.title.contains(q, ignoreCase = true)

            val matchAuthor = book.authors
                ?.any { author -> author.contains(q, ignoreCase = true) } ?: false

            matchTitle || matchAuthor
        }
        bookSearchAdapter.submitList(filtered)

    }

    private fun setupListeners() = with(binding) {
        btnAddPhoto.setOnClickListener {
            // TODO: 갤러리/카메라 선택 로직 붙이기 (ActivityResult API)
        }

        btnSubmit.setOnClickListener {
            submitReview()
        }
    }


    private fun submitReview() = with(binding) {
        val title = etBookTitle.text?.toString()?.trim().orEmpty()
        val authorName = etAuthor.text?.toString()?.trim().orEmpty()
        val body = etBody.text?.toString()?.trim().orEmpty()
        val publisher = etPublisher.text?.toString()?.trim().orEmpty()
        val isbn = etIsbn.text?.toString()?.trim().orEmpty()

        if (!validate(title, body)) return@with

        val newReview = PostReview(
            bookTitle = title,
            content = body,
            authorName = authorName,
            publisher = publisher,
            isbn = isbn,
            imageUrls = selectedUrls.map { it.toString() },
            bookId = selectedBookId
        )

        parentViewModel.addNewReview(newReview)

        findNavController().previousBackStackEntry
            ?.savedStateHandle
            ?.set("shouldRefreshHome", true)

        findNavController().popBackStack()
    }


    private fun validate(title: String, body: String): Boolean {
        if (title.isBlank()) {
            return false
        }
        if (body.isBlank()) {
            return false
        }
        return true
    }

    private fun togglePhotoViews() {
        val hasItems = selectedUrls.isNotEmpty()
        binding.rvPhotos.isVisible = hasItems
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
