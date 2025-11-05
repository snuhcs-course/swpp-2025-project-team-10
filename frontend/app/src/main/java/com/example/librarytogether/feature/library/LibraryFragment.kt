package com.example.librarytogether.feature.library
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.transition.AutoTransition
import androidx.transition.TransitionManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentLibraryBinding
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.tabs.TabLayout
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LibraryFragment : Fragment() {

    private val viewModel: LibraryViewModel by activityViewModels()
    private var _binding: FragmentLibraryBinding? = null
    private val binding get() = _binding!!

    private var isEditingProfile: Boolean = false

    private val reviewAdapter by lazy { ReviewAdapter(
        clicks = ReviewClicks(
            onClickLike = { review ->
                viewModel.toggleLike(review)
            },
        )
    ) }

    private val bookRowAdapter by lazy { BookAdapter(
        mode = BookListMode.ROW,
        clicks = BookClicks(
            onClickItem = { book ->
                // TODO: 책 상세 화면으로 이동
                Toast.makeText(requireContext(), "책 상세 화면으로 이동", Toast.LENGTH_SHORT).show()
            }
        )
    )}

    private val bookTileAdapter by lazy { BookAdapter(
        mode = BookListMode.TILE,
        clicks = BookClicks(
            onClickItem = { book ->
                // TODO: 책 상세 화면으로 이동
                Toast.makeText(requireContext(), "책 상세 화면으로 이동", Toast.LENGTH_SHORT).show()
            }
        )
    )}

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = FragmentLibraryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupClickListeners()
        setupTabs()
        observeViewModel()

    }

    private fun setupClickListeners() {
        binding.btnAddWishlist.setOnClickListener {
            // TODO: 책 검색 화면으로 이동
            Toast.makeText(requireContext(), "책 검색 화면으로 이동", Toast.LENGTH_SHORT).show()
        }

        binding.btnManageWishlist.setOnClickListener {
            // TODO: Adapter에 관리 모드 전달
        }
    }

    private fun observeViewModel() {
        viewModel.myReviews.observe(viewLifecycleOwner) { reviews ->
            reviewAdapter.submitList(reviews)
            val isReviewTabActive = binding.contentTabs.selectedTabPosition == 0

            if (reviews.isEmpty()) {
                binding.rvReviews.visibility = View.GONE
                binding.tvReviewEmpty.visibility = if (isReviewTabActive) View.VISIBLE else View.GONE
            } else {
                binding.rvReviews.visibility = if (isReviewTabActive) View.VISIBLE else View.GONE
                binding.tvReviewEmpty.visibility = View.GONE
            }
        }

        viewModel.myBooks.observe(viewLifecycleOwner) { books ->
            bookTileAdapter.submitList(books)
            val isBookTabActive = binding.contentTabs.selectedTabPosition == 1

            if (books.isEmpty()) {
                binding.rvBooks.visibility = View.GONE
                binding.tvBookEmpty.visibility = if (isBookTabActive) View.VISIBLE else View.GONE
            } else {
                binding.rvBooks.visibility = if (isBookTabActive) View.VISIBLE else View.GONE
                binding.tvBookEmpty.visibility = View.GONE
            }
        }

        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            if (profile == null) return@observe

            val fieldPlaceholder = getString(R.string.profile_field_empty)
            val bioPlaceholder = getString(R.string.profile_bio_empty)

            binding.tvName.text = profile.username
            binding.tvBio.text = profile.bio.takeIf { !it.isNullOrEmpty() } ?: bioPlaceholder
            binding.ivProfileImage.loadAvatar(profile.profileUrl)
            binding.tvReviewCount.text = profile.reviewCount.toString()
            binding.tvFollowerCount.text = profile.followerCount.toString()
            binding.tvFollowingCount.text = profile.followingCount.toString()

            binding.tvTradeLocation1.text = profile.preferences.tradeLocation1
            binding.tvTradeLocation2.text = profile.preferences.tradeLocation2
            binding.tvTradeSpot1.text = profile.preferences.tradeSpot1
            binding.tvTradeSpot2.text = profile.preferences.tradeSpot2
            binding.tvFavBook.text = profile.preferences.favBook
            binding.tvFavBookNote.text = profile.preferences.favBookNote
            binding.tvFavAuthor.text = profile.preferences.favAuthor
            binding.tvFavAuthorNote.text = profile.preferences.favAuthorNote
            binding.tvReadingHabit.text = profile.preferences.readingHabit
            binding.tvGenreNone.visibility = if (profile.favoriteGenres.isEmpty()) View.VISIBLE else View.GONE

            renderSelectedGenresFromViewModel(profile.favoriteGenres)
            syncEditChipsFromViewModel(profile.favoriteGenres)
        }

        viewModel.myWishlist.observe(viewLifecycleOwner) { books ->
            bookRowAdapter.submitList(books)

            if (books.isEmpty()) {
                binding.rvWishlist.visibility = View.GONE
                binding.tvWishlistEmpty.visibility = View.VISIBLE
            } else {
                binding.rvWishlist.visibility = View.VISIBLE
                binding.tvWishlistEmpty.visibility = View.GONE
            }
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
//            binding.progressBar.isVisible = isLoading
        }

        viewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(requireContext(), it, Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun setupRecyclerView() {
        binding.rvReviews.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = reviewAdapter
            setHasFixedSize(true)
        }

        binding.rvBooks.apply {
            layoutManager = GridLayoutManager(requireContext(), 3)
            adapter = bookTileAdapter
            setHasFixedSize(true)
        }

        binding.rvWishlist.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = bookRowAdapter
            setHasFixedSize(true)
        }
    }

    private fun setupTabs() {
        binding.contentTabs.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> {
                        binding.rvReviews.visibility = View.VISIBLE
                        binding.rvBooks.visibility = View.GONE
                        binding.profileContainer.visibility = View.GONE
                        updateFabForTab(0, isEditingProfile)
                    }
                    1 -> {
                        binding.rvReviews.visibility = View.GONE
                        binding.rvBooks.visibility = View.VISIBLE
                        binding.profileContainer.visibility = View.GONE
                        updateFabForTab(1, isEditingProfile)
                    }
                    2 -> {
                        binding.rvReviews.visibility = View.GONE
                        binding.rvBooks.visibility = View.GONE
                        binding.profileContainer.visibility = View.VISIBLE
                        updateFabForTab(2, isEditingProfile)
                    }
                }
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {
            }

            override fun onTabReselected(tab: TabLayout.Tab?) {
            }
        })

        binding.rvReviews.visibility = View.VISIBLE
        binding.rvBooks.visibility = View.GONE
        binding.profileContainer.visibility = View.GONE
        updateFabForTab(0, isEditingProfile)
    }

    // SetupTabs helper functions start

    private fun updateFabForTab(index: Int, editing: Boolean) = with(binding.fabAdd) {
        when (index) {
            0 -> { // 리뷰 탭
                setImageResource(R.drawable.plus_icon)
                contentDescription = getString(R.string.fab_add_review)
                setOnClickListener {
                    findNavController().navigate(R.id.action_libraryFragment_to_writeReviewFragment)
                }
            }
            1 -> { // 책장 탭
                setImageResource(R.drawable.plus_icon)
                contentDescription = getString(R.string.fab_add_book)
                setOnClickListener {
                    findNavController().navigate(R.id.action_libraryFragment_to_addBookFragment)
                }
                show()
            }
            2 -> { // 프로필 탭
                if (editing) {
                    setImageResource(R.drawable.check_icon) // 완료
                    contentDescription = getString(R.string.fab_save_profile)
                    setOnClickListener {
                        val currentProfile = viewModel.userProfile.value ?: return@setOnClickListener

                        val selectedGenres = getSelectedGenresFromEdit()

                        val newPrefs = currentProfile.preferences.copy(
                            tradeLocation1 = binding.editTradeLocation1.text.toString(),
                            tradeLocation2 = binding.editTradeLocation2.text.toString(),
                            tradeSpot1 = binding.editTradeSpot1.text.toString(),
                            tradeSpot2 = binding.editTradeSpot2.text.toString(),
                            favBook = binding.editFavBook.text.toString(),
                            favBookNote = binding.editFavBookNote.text.toString(),
                            favAuthor = binding.editFavAuthor.text.toString(),
                            favAuthorNote = binding.editFavAuthorNote.text.toString(),
                            readingHabit = binding.editReadingHabit.text.toString()
                        )

                        val newProfile = currentProfile.copy(
                            preferences = newPrefs,
                            favoriteGenres = selectedGenres
                        )

                        viewModel.saveProfile(newProfile)
                        toggleProfileEdit(false)
                    }
                } else {
                    setImageResource(R.drawable.edit_icon)  // 편집
                    contentDescription = getString(R.string.fab_edit_profile)
                    setOnClickListener {
                        toggleProfileEdit(true)
                    }
                }
                show()
            }
        }
    }

    private fun toggleProfileEdit(edit: Boolean): Unit = with(binding){
        isEditingProfile = edit

        TransitionManager.beginDelayedTransition(profileRoot as ViewGroup, AutoTransition())

        // 1) 보기/편집 뷰 묶음 전환 -------------------------------

        setGroupVisible(
            edit = edit,
            viewViews = listOf(tvTradeLocation1, tvTradeLocation2, tvTradeSpot1, tvTradeSpot2),
            editViews = listOf(editTradeLocation1, editTradeLocation2, editTradeSpot1, editTradeSpot2)
        )

        groupSelectedGenres.visibility = if (edit) View.GONE else View.VISIBLE
        chipGroupGenres.visibility     = if (edit) View.VISIBLE else View.GONE

        setGroupVisible(
            edit = edit,
            viewViews = listOf(tvFavBook, tvFavBookNote),
            editViews = listOf(editFavBook, editFavBookNote)
        )

        setGroupVisible(
            edit = edit,
            viewViews = listOf(tvFavAuthor, tvFavAuthorNote),
            editViews = listOf(editFavAuthor, editFavAuthorNote)
        )

        setGroupVisible(
            edit = edit,
            viewViews = listOf(tvReadingHabit),
            editViews = listOf(editReadingHabit)
        )

        btnManageWishlist.visibility = if (edit) View.VISIBLE else View.GONE
        btnAddWishlist.visibility = if (edit) View.VISIBLE else View.GONE

        // 2) 값 동기화

        if (edit) {
            // 보기 → 편집 (진입 시)
            val profile = viewModel.userProfile.value ?: return
            editTradeLocation1.setText(profile.preferences.tradeLocation1)
            editTradeLocation2.setText(profile.preferences.tradeLocation2)
            editTradeSpot1.setText(profile.preferences.tradeSpot1)
            editTradeSpot2.setText(profile.preferences.tradeSpot2)
            editFavBook.setText(profile.preferences.favBook)
            editFavBookNote.setText(profile.preferences.favBookNote)
            editFavAuthor.setText(profile.preferences.favAuthor)
            editFavAuthorNote.setText(profile.preferences.favAuthorNote)
            editReadingHabit.setText(profile.preferences.readingHabit)
            syncEditChipsFromViewModel(profile.favoriteGenres)

            editTradeLocation1.requestFocus()

        } else {

            hideKeyboard()
        }

        // 3) FAB 상태 갱신
        updateFabForTab(2, isEditingProfile)
    }

    private fun setGroupVisible(
        edit: Boolean,
        viewViews: List<View>,
        editViews: List<View>
    ) {
        viewViews.forEach { it.visibility = if (edit) View.GONE else View.VISIBLE }
        editViews.forEach { it.visibility = if (edit) View.VISIBLE else View.GONE }
    }

     private fun hideKeyboard() {
        val imm = requireContext().getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        view?.let { v -> imm.hideSoftInputFromWindow(v.windowToken, 0) }
    }

    private fun getSelectedGenresFromEdit(): List<String> = with(binding) {
        val selected = mutableListOf<String>()
        for (i in 0 until chipGroupGenres.childCount) {
            val c = chipGroupGenres.getChildAt(i)
            if (c is com.google.android.material.chip.Chip && c.isChecked) {
                selected.add(c.text?.toString().orEmpty())
            }
        }
        return selected
    }

    private fun renderSelectedGenresFromViewModel(genres: List<String>) {
        binding.groupSelectedGenres.removeAllViews()
        if (genres.isEmpty()) {
            binding.tvGenreNone.visibility = View.VISIBLE
        } else {
            binding.tvGenreNone.visibility = View.GONE
            genres.forEach { label ->
                binding.groupSelectedGenres.addView(makeAssistChip(label))
            }
        }
    }

    private fun makeAssistChip(text: String, muted: Boolean = false): com.google.android.material.chip.Chip {
        return com.google.android.material.chip.Chip(requireContext()).apply {
            this.text = text
            isCheckable = false
            isClickable = false
            if (muted) {
                setTextAppearance(R.style.Text_Body)
            }
        }
    }

    private fun syncEditChipsFromViewModel(genres: List<String>) {
        val genreSet = genres.toSet()
        for (i in 0 until binding.chipGroupGenres.childCount) {
            val c = binding.chipGroupGenres.getChildAt(i)
            if (c is com.google.android.material.chip.Chip) {
                c.isChecked = genreSet.contains(c.text.toString())
            }
        }
    }
}
