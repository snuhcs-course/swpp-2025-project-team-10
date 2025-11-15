package com.example.librarytogether.feature.home
import android.os.Bundle
import android.view.View
import android.widget.PopupMenu
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentHomeBinding
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.feature.library.LibraryViewModel
import com.example.librarytogether.feature.library.data.Book
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val homeviewModel: HomeViewModel by viewModels()
    private val libraryViewModel: LibraryViewModel by activityViewModels()
    private val feedAdapter: FeedAdapter by lazy { FeedAdapter(
        FeedClicks(
            onClickLike = homeviewModel::toggleLike,
            onClickAdd = ::onClickAddToWishlist,
            onClickReview =:: navigateToReview,
            onClickExchange =:: onClickExchange,
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
                    homeviewModel.loadFeed()
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
                    R.id.sort_latest -> homeviewModel.applySort(SortType.LATEST)
                    R.id.sort_popular -> homeviewModel.applySort(SortType.POPULAR)
                }
                true
            }
            popup.show()
        }
    }

    private fun observeViewModel() {
        homeviewModel.posts.observe(viewLifecycleOwner) { posts ->
            feedAdapter.submitList(posts)
        }

        homeviewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
                homeviewModel.onErrorShown()
            }
        }
        homeviewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
//            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        homeviewModel.barterLoading.observe(viewLifecycleOwner) { loading ->
            binding.rvFeed.isEnabled = !loading
        }
        homeviewModel.barterSuccess.observe(viewLifecycleOwner) { ok ->
            if (ok == true) {
                Snackbar.make(requireView(), "교환 신청을 보냈습니다.", Snackbar.LENGTH_SHORT).show()
                homeviewModel.clearBarterResult()
            }
        }
        homeviewModel.barterError.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrBlank()) {
                Snackbar.make(requireView(), msg, Snackbar.LENGTH_SHORT).show()
                homeviewModel.clearBarterResult()
            }
        }

        libraryViewModel.error.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrBlank()) {
                Snackbar.make(requireView(), msg, Snackbar.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun onClickAddToWishlist(post: Post) {
        libraryViewModel.toggleWishlistById(post.bookId)
//        Snackbar.make(requireView(), "위시리스트에 추가했습니다.", Snackbar.LENGTH_SHORT).show()
    }

    private fun navigateToReview(post: Post) {
        Toast.makeText(requireContext(), "서평", Toast.LENGTH_SHORT).show()
        // TODO: 서평 댓글 화면으로 이동
    }

    private fun onClickExchange(post: Post) {
        val ownerName = post.posterName
        val ownerId = post.posterId
        val bookId = post.bookId

        val title = getString(R.string.barter_title_to_user, ownerName)

        MaterialAlertDialogBuilder(requireContext())
            .setTitle(title)
            .setMessage(getString(R.string.barter_confirm_msg))
            .setNegativeButton(getString(R.string.cancel), null)
            .setPositiveButton(getString(R.string.barter_apply)) { _, _ ->
                homeviewModel.requestBarter(ownerId, bookId)
            }
            .show()
    }

    private fun navigateToProfile(post: Post) {
        val action = HomeFragmentDirections.actionGlobalToUserProfileFragment(
            userId = post.posterId
        )
        findNavController().navigate(action)
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
