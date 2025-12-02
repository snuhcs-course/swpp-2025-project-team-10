package com.example.librarytogether.feature.profile

import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.observe
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentUserProfileBinding
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.BookAdapter
import com.example.librarytogether.feature.library.BookClicks
import com.example.librarytogether.feature.library.BookListMode
import com.example.librarytogether.feature.library.LibraryFragment
import com.example.librarytogether.feature.library.ReviewAdapter
import com.example.librarytogether.feature.library.ReviewClicks
import com.example.librarytogether.feature.profile.UserProfileFragmentArgs
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.tabs.TabLayout
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class UserProfileFragment : Fragment(R.layout.fragment_user_profile) {
    private var _binding: FragmentUserProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ProfileViewModel by viewModels()
    private val args: UserProfileFragmentArgs by navArgs() // userId 전달

    private enum class Tab { REVIEWS, BOOKS, PROFILE }
    private var currentTab: Tab = Tab.REVIEWS

    private var isReviewEmpty = true
    private var isBookEmpty = true
    private var isWishlistEmpty = true

    private val wishlistAdapter by lazy {
        BookAdapter(
            mode = BookListMode.ROW,
            clicks = BookClicks(
                onClickItem = { book ->
                    val dir = BookDetailFragmentDirections
                        .actionGlobalBookDetail(
                            bookId = book.id,
                            source = EntrySource.WISHLIST
                        )
                    findNavController().navigate(dir)
                }
            )
        )
    }
    private val booksAdapter by lazy {
        BookAdapter(
            mode = BookListMode.TILE,
            clicks = BookClicks(
                onClickItem = { book ->
                    val dir = BookDetailFragmentDirections
                        .actionGlobalBookDetail(
                            bookId = book.id,
                            source = EntrySource.BOOKSHELF
                        )
                    findNavController().navigate(dir)
                }
            )
        )
    }

    private val reviewAdapter by lazy {
        ReviewAdapter(
            clicks = ReviewClicks(
                onClickLike = { review ->
                    viewModel.toggleLike(review.id)
                },
            )
        )
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentUserProfileBinding.bind(view)
        binding.toolbar.setNavigationOnClickListener {
            findNavController().navigateUp()
        }

        viewModel.loadUserProfile(args.userId)

        setupRecyclerViews()
        setupClickListeners()
        setupTabs()
        observeViewModel()

        render()
    }

    private fun setupClickListeners() {
        binding.btnFollow.setOnClickListener {
            viewModel.toggleFollow()
        }
    }

    private fun setupTabs() {
        binding.contentTabs.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                currentTab = when (tab?.position) {
                    0 -> Tab.REVIEWS
                    1 -> Tab.BOOKS
                    else -> Tab.PROFILE
                }
                render()
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
        val index = when (currentTab) {
            Tab.REVIEWS -> 0
            Tab.BOOKS   -> 1
            Tab.PROFILE -> 2
        }
        binding.contentTabs.getTabAt(index)?.select()
    }

    private fun setupRecyclerViews() {
        binding.rvReviews.adapter = reviewAdapter
        binding.rvBooks.adapter = booksAdapter
        binding.rvWishlist.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = wishlistAdapter
            setHasFixedSize(true)
        }
    }

    private fun render() = with(binding) {
        rvReviews.visibility       = if (currentTab == Tab.REVIEWS && !isReviewEmpty) View.VISIBLE else View.GONE
        tvReviewEmpty.visibility   = if (currentTab == Tab.REVIEWS &&  isReviewEmpty) View.VISIBLE else View.GONE

        rvBooks.visibility         = if (currentTab == Tab.BOOKS   && !isBookEmpty)   View.VISIBLE else View.GONE
        tvBookEmpty.visibility     = if (currentTab == Tab.BOOKS   &&  isBookEmpty)   View.VISIBLE else View.GONE

        profileContainer.visibility = if (currentTab == Tab.PROFILE) View.VISIBLE else View.GONE

        profileContainer.visibility = if (currentTab == Tab.PROFILE) View.VISIBLE else View.GONE

        if (currentTab == Tab.PROFILE) {
            rvWishlist.visibility       = if (!isWishlistEmpty) View.VISIBLE else View.GONE
            tvWishlistEmpty.visibility  = if (isWishlistEmpty)  View.VISIBLE else View.GONE
        } else {
            rvWishlist.visibility = View.GONE
            tvWishlistEmpty.visibility = View.GONE
        }
    }

    private fun observeViewModel() {
        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            if (profile == null) return@observe

            binding.tvName.text = profile.username
            binding.tvBio.text = profile.preferences.readingHabit?.ifEmpty { "소개가 없습니다." }
            binding.ivProfileImage.loadAvatar(profile.profileUrl)
            binding.tvReviewCount.text = profile.reviewCount.toString()
            binding.tvFollowerCount.text = profile.followerCount.toString()
            binding.tvFollowingCount.text = profile.followingCount.toString()

            binding.tvTradeLocation1.text = profile.preferences.tradeLocation1
            binding.tvTradeSpot1.text = profile.preferences.tradeSpot1
            binding.tvFavBook.setTextOrGone(profile.preferences.favBooks?.firstOrNull())
            binding.tvFavBookNote.setTextOrGone(profile.preferences.favBookNotes?.firstOrNull())
            binding.tvFavAuthor.setTextOrGone(profile.preferences.favAuthors?.firstOrNull())
            binding.tvFavAuthorNote.setTextOrGone(profile.preferences.favAuthorNotes?.firstOrNull())
            binding.tvReadingHabit.text = profile.preferences.readingHabit

            binding.btnFollow.text = if (profile.isFollowing) {
                getString(R.string.unfollow)
            } else {
                getString(R.string.follow)
            }
        }

        viewModel.reviews.observe(viewLifecycleOwner) { reviews ->
            reviewAdapter.submitList(reviews)
            isReviewEmpty = reviews.isEmpty()
            render()
        }

        viewModel.books.observe(viewLifecycleOwner) { books ->
            booksAdapter.submitList(books)
            isBookEmpty = books.isEmpty()
            render()
        }

        viewModel.wishlist.observe(viewLifecycleOwner) { wishlist ->
            wishlistAdapter.submitList(wishlist)
            isWishlistEmpty = wishlist.isEmpty()
            render()
        }

        viewModel.loading.observe(viewLifecycleOwner) { isLoading ->
            //binding.progressBar.isVisible = isLoading
        }

        viewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun TextView.setTextOrGone(value: String?) {
        if (value.isNullOrBlank()) {
            visibility = View.GONE
        } else {
            visibility = View.VISIBLE
            text = value
        }
    }

    override fun onDestroyView() {
        _binding = null
        super.onDestroyView()
    }
}
