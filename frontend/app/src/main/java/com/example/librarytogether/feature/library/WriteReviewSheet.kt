package com.example.librarytogether.feature.library

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.viewModels
import com.example.librarytogether.R
import com.example.librarytogether.databinding.WriteReviewSheetBinding
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.postReview
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class WriteReviewSheet : BottomSheetDialogFragment(R.layout.write_review_sheet) {

    private val parentViewModel: LibraryViewModel by viewModels({ requireParentFragment() })

    private var _binding: WriteReviewSheetBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = WriteReviewSheetBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val behavior = BottomSheetBehavior.from(requireView().parent as View)
        behavior.state = BottomSheetBehavior.STATE_EXPANDED

        binding.btnSubmit.setOnClickListener {
            val title = binding.etBookTitle.text.toString()
            val authorName = binding.etAuthor.text.toString()
            val body = binding.etBody.text.toString()

            val newReview = postReview(
                bookTitle = title,
                content = body,
                authorName = authorName,
                imageUrls = emptyList()
            )

            parentViewModel.addNewReview(newReview)

            dismiss()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}