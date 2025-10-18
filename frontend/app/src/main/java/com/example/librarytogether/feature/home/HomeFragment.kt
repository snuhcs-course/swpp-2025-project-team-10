package com.example.librarytogether.feature.home
import android.os.Bundle
import android.view.View
import android.widget.PopupMenu
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentHomeBinding
import com.example.librarytogether.feature.home.data.Post
import com.example.librarytogether.network.RetrofitClient
import com.example.librarytogether.feature.home.data.HomeApi
import kotlinx.coroutines.launch

class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private val feedAdapter by lazy { FeedAdapter(
        FeedClicks(
            onClickLike =:: onClickLike,
            onClickReview =:: onClickReview,
            onClickExchange =:: onClickExchange,
            onClickAdd =:: onClickAdd,
            onClickMore =:: onClickMore,
            onClickProfile =:: onClickProfile,
            onClickUserName =:: onClickUserName,
            onClickTitle =:: onClickTitle,
            onClickAuthor =:: onClickAuthor,
            onClickContent =:: onClickContent,
        )
    ) }

    private var currentPosts: List<Post> = emptyList()

    private val service: HomeApi by lazy {
        RetrofitClient.getClient(requireContext()).create(HomeApi::class.java)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        setupRecyclerView()
        setupSortButton()
        loadFeed()
    }

    private fun setupRecyclerView() {
        binding.rvFeed.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = feedAdapter
            setHasFixedSize(true)
        }
    }

    private fun setupSortButton() {
        binding.ivSort.setOnClickListener { anchorView ->
            val popup = PopupMenu(requireContext(), anchorView)
            popup.menuInflater.inflate(R.menu.menu_feed_sort, popup.menu)
            popup.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    R.id.sort_latest -> applySort(SortType.LATEST)
                    R.id.sort_popular -> applySort(SortType.POPULAR)
                }
                true
            }
            popup.show()
        }
    }

    private fun loadFeed() {
        lifecycleScope.launch {
            val response = service.feed()
            if (response.isSuccessful) {
                val posts = response.body()?.results ?: emptyList()
                currentPosts = posts
                applySort(SortType.LATEST)
            }
        }
    }

    // TODO: 가까운순 추가
    private enum class SortType { LATEST, POPULAR }

    private fun applySort(type: SortType) {
        if (currentPosts.isEmpty()) return

        val sorted = when (type) {
            SortType.LATEST -> currentPosts.sortedByDescending { it.createdAt }
            SortType.POPULAR -> currentPosts.sortedByDescending { it.likeCount }
        }
        feedAdapter.submitList(sorted.toList())
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun onClickLike(post: Post) {
        lifecycleScope.launch {
            try {
                val response = service.likePost(post.id)
                if (response.isSuccessful) {
                    val updatedPost = response.body()?.post
                    val updatedList = currentPosts.map {
                        if (it.id == updatedPost?.id) updatedPost else it
                    }
                    currentPosts = updatedList
                } else {
                    Toast.makeText(requireContext(), "좋아요 처리에 실패.", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "네트워크 오류.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun onClickReview(post: Post) {
        Toast.makeText(requireContext(), "서평", Toast.LENGTH_SHORT).show()
        // TODO: 서평 작성 화면으로 이동
    }

    private fun onClickExchange(post: Post) {
        Toast.makeText(requireContext(), "교환", Toast.LENGTH_SHORT).show()
        // TODO: 교환 화면으로 이동
    }

    private fun onClickAdd(post: Post) {
        Toast.makeText(requireContext(), "찜하기", Toast.LENGTH_SHORT).show()
        // TODO: 찜하기 기능 구현
    }

    private fun onClickMore(post: Post) {
        Toast.makeText(requireContext(), "메뉴", Toast.LENGTH_SHORT).show()
        // TODO: 메뉴 구현
    }

    private fun onClickProfile(post: Post) {
        Toast.makeText(requireContext(), "유저", Toast.LENGTH_SHORT).show()
        // TODO: 유저 프로필 화면으로 이동
    }

    private fun onClickUserName(post: Post) = onClickProfile(post)

    private fun onClickTitle(post: Post) {
        Toast.makeText(requireContext(), "제목", Toast.LENGTH_SHORT).show()
        // TODO: 제목 클릭 시 상세 페이지로 이동
    }

    private fun onClickAuthor(post: Post) {
        Toast.makeText(requireContext(), "작가", Toast.LENGTH_SHORT).show()
        // TODO: 작가 클릭 시 작가 프로필 화면으로 이동
    }

    private fun onClickContent(post: Post) {
        feedAdapter.toggleExpand(post.id)
    }
}