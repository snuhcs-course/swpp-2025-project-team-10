package com.example.librarytogether.feature.barter

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.navGraphViewModels
import androidx.recyclerview.widget.GridLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentSelectMyBookBinding
import com.example.librarytogether.feature.library.BookAdapter
import com.example.librarytogether.feature.library.BookClicks
import com.example.librarytogether.feature.library.BookListMode

class SelectMyBookFragment : Fragment(R.layout.fragment_select_my_book) {

    private var _binding: FragmentSelectMyBookBinding? = null
    private val binding get() = _binding!!

    private val viewModel: BarterDetailViewModel by navGraphViewModels(R.id.nav_barter_flow)

    private val bookTileAdapter by lazy { BookAdapter(
        mode = BookListMode.TILE,
        clicks = BookClicks(
            onClickItem = { book ->
                viewModel.selectBook(book)
                findNavController().popBackStack()
            }
        )
    )}

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentSelectMyBookBinding.bind(view)

        // 5. '내 책' 목록을 불러오는 API가 ViewModel에 필요함
        //    (BarterDetailViewModel에 getMyBooks() 함수 추가 필요)
        //    viewModel.loadMyBooks()

        setupRecyclerView()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        binding.rvMyBooks.apply {
            layoutManager = GridLayoutManager(requireContext(), 3)
            adapter = bookTileAdapter
        }
    }

    private fun observeViewModel() {
        // 6. ViewModel의 'myBooks' LiveData를 구독
        viewModel.myBooks.observe(viewLifecycleOwner) { books ->
            bookTileAdapter.submitList(books)
            // (empty view 처리 등)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
