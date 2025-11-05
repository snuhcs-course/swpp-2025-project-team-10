package com.example.librarytogether.feature.home
import android.os.Bundle
import android.view.View
import android.widget.PopupMenu
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.NavigationGraphDirections
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentHomeBinding
import com.example.librarytogether.feature.home.data.Post
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()
    private val feedAdapter: FeedAdapter by lazy { FeedAdapter(
        FeedClicks(
            onClickLike = viewModel::toggleLike,
            onClickAdd = viewModel::onClickAdd,

            onClickReview =:: navigateToReview,
            onClickExchange =:: navigateToExchange,
            onClickMore =:: showMoreOptions,
            onClickProfile =:: navigateToProfile,
            onClickUserName =:: navigateToProfile,
            onClickTitle =:: searchTitle,
            onClickAuthor =:: searchAuthor,
            onClickContent =:: expandContent,
        )
    ) }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        setupRecyclerView()
        setupSortButton()
        observeViewModel()

        // new rv 작성 후 돌아왔을 때만 home feed refresh + scroll to top
        findNavController().currentBackStackEntry
            ?.savedStateHandle
            ?.getLiveData<Boolean>("shouldRefreshHome")
            ?.observe(viewLifecycleOwner) { shouldRefresh ->
                if (shouldRefresh == true) {
                    viewModel.loadFeed()
                    binding.rvFeed.scrollToPosition(0)
                }
            }
    }

    private fun setupRecyclerView() {
        binding.rvFeed.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = feedAdapter
        }
    }

    private fun setupSortButton() {
        binding.ivSort.setOnClickListener { anchorView ->
            val popup = PopupMenu(requireContext(), anchorView)
            popup.menuInflater.inflate(R.menu.menu_feed_sort, popup.menu)
            popup.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    R.id.sort_latest -> viewModel.applySort(SortType.LATEST)
                    R.id.sort_popular -> viewModel.applySort(SortType.POPULAR)
                }
                true
            }
            popup.show()
        }
    }

    private fun observeViewModel() {
        viewModel.posts.observe(viewLifecycleOwner) { posts ->
            feedAdapter.submitList(posts)
        }

        viewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                viewModel.onErrorShown()
            }
        }
        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
//            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun navigateToReview(post: Post) {
        Toast.makeText(requireContext(), "서평", Toast.LENGTH_SHORT).show()
        // TODO: 서평 댓글 화면으로 이동
    }

    private fun navigateToExchange(post: Post) {
        val userBookId = post.userBookId
        val action = NavigationGraphDirections.actionGlobalToBarterDetailFragment(userBookId)

        findNavController().navigate(action)
    }

    private fun navigateToProfile(post: Post) {
        Toast.makeText(requireContext(), "찜하기", Toast.LENGTH_SHORT).show()
        // TODO: 찜하기 기능 구현
    }

    private fun showMoreOptions(post: Post) {
        Toast.makeText(requireContext(), "메뉴", Toast.LENGTH_SHORT).show()
        // TODO: 메뉴 구현
    }

    private fun searchTitle(post: Post) {
        Toast.makeText(requireContext(), "제목", Toast.LENGTH_SHORT).show()
        // TODO: 제목 클릭 시 제목 검색
    }

    private fun searchAuthor(post: Post) {
        Toast.makeText(requireContext(), "작가", Toast.LENGTH_SHORT).show()
        // TODO: 작가 클릭 시 작가 검색
    }

    private fun expandContent(post: Post) {
        feedAdapter.toggleExpand(post.id)
    }
}
