package com.example.librarytogether.feature.library

import android.net.Uri
import android.os.Bundle
import android.view.View
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentWriteReviewBinding
import com.example.librarytogether.feature.library.data.PostReview
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class WriteReviewFragment : Fragment(R.layout.fragment_write_review) {

    private val parentViewModel: LibraryViewModel by activityViewModels()

    private val selectedUrls = mutableListOf<Uri>()
    private lateinit var photoAdapter: PhotoAdapter

    private var _binding: FragmentWriteReviewBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentWriteReviewBinding.bind(view)

        setupRecyclerView()
        setupListeners()
        submitReview()

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
    }

    private fun setupListeners() = with(binding) {
        btnAddPhoto.setOnClickListener {
            // TODO: 갤러리/카메라 선택 로직 붙이기 (ActivityResult API)
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
            imageUrls = selectedUrls.map { it.toString() }
        )

        parentViewModel.addNewReview(newReview)
// 수정 전
//        requireActivity().onBackPressedDispatcher.onBackPressed()
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
