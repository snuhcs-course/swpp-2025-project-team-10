package com.example.librarytogether.feature.barter

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.navigation.navGraphViewModels
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentBarterDetailBinding
import com.example.librarytogether.util.loadAvatar
import com.example.librarytogether.util.loadCover
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class BarterDetailFragment : Fragment(R.layout.fragment_barter_detail) {

    private var _binding: FragmentBarterDetailBinding? = null
    private val binding get() = _binding!!

    private val viewModel: BarterDetailViewModel by navGraphViewModels(R.id.nav_barter_flow)

    private val args by navArgs<BarterDetailFragmentArgs>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentBarterDetailBinding.bind(view)

        setupClickListeners()
        observeViewModel()

        viewModel.loadDetails(args.userBookId)
    }

    private fun setupClickListeners() {
        binding.btnBack.setOnClickListener {
            findNavController().popBackStack()
        }

        binding.btnSelectFromLibrary.setOnClickListener {
            findNavController().navigate(R.id.action_barterDetailFragment_to_selectMyBookFragment)
        }

        binding.btnChangeBook.setOnClickListener {
            findNavController().navigate(R.id.action_barterDetailFragment_to_selectMyBookFragment)
        }

        binding.btnRegisterNewBook.setOnClickListener {
            // TODO: 새 책 등록 화면으로 이동
        }

        binding.btnSubmitExchange.setOnClickListener {
            val message = binding.etOfferMessage.text.toString()
            viewModel.submitOffer(message) // ViewModel의 submitOffer 호출 (기존과 동일)
        }
    }

    private fun observeViewModel() {
        viewModel.barterDetails.observe(viewLifecycleOwner) { detail ->
            if (detail == null) return@observe

            binding.tvPoster.text = detail.owner.username
            binding.ivProfileImage.loadAvatar(detail.owner.profileUrl)

            binding.tvBookTitleWant.text = detail.book.title
            binding.tvBookAuthorWant.text = detail.book.author

             binding.ivBookCoverWant.loadCover(detail.book.coverUrl)
        }

        viewModel.selectedBook.observe(viewLifecycleOwner) { book ->
            val isBookSelected = (book != null)

            binding.selectionButtonsContainer.isVisible = !isBookSelected
            binding.selectedBookContainer.isVisible = isBookSelected

            binding.btnChangeBook.isVisible = isBookSelected

            if (book != null) {
                binding.tvBookTitleOffer.text = book.title
                binding.tvBookAuthorOffer.text = book.author
                 binding.ivBookCoverOffer.loadCover(book.coverUrl)
            }
        }

        // 8. 'navigateToOfferComplete' observe 로직 (기존과 동일, 매우 중요)
        viewModel.navigateToOfferComplete.observe(viewLifecycleOwner) { hasCompleted ->
            if (hasCompleted) {
                Toast.makeText(requireContext(), "교환 신청 완료!", Toast.LENGTH_SHORT).show()
                findNavController().popBackStack() // 임시로 뒤로가기

                // 이벤트 중복 실행을 막기 위해 ViewModel에 완료되었음을 알림
                viewModel.onNavigationComplete()
            }
        }

        viewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let { Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show() }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
