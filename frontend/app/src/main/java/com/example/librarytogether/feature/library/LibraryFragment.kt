package com.example.librarytogether.feature.library
import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.TextView
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
import com.example.librarytogether.feature.bookdetail.BookDetailFragmentDirections
import com.example.librarytogether.feature.bookdetail.EntrySource
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.util.loadAvatar
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.tabs.TabLayout
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LibraryFragment : Fragment() {

    private val viewModel: LibraryViewModel by activityViewModels()
    private var _binding: FragmentLibraryBinding? = null
    private val binding get() = _binding!!

    private var isEditingProfile: Boolean = false

    private var isReviewEmpty = true
    private var isBookEmpty = true
    private var isWishlistEmpty = true
    private var isGenreEmpty = true

    private val selectedLocations = mutableListOf<Pair<String, String>>()

    private enum class Tab { REVIEWS, BOOKS, PROFILE }
    private var currentTab: Tab = Tab.REVIEWS

    private val reviewAdapter by lazy { ReviewAdapter(
        clicks = ReviewClicks(
            onClickLike = { review ->
                viewModel.toggleLike(review)
            },
            onClickEdit = { review ->
                navigateToEditReview(review)
            },
            onClickDelete = { review ->
                confirmDeleteReview(review)
            },
        )
    ) }

    private val bookRowAdapter by lazy {
        BookAdapter(
            mode = BookListMode.ROW,
            clicks = BookClicks(
                onClickItem = { book ->
                    val dir = BookDetailFragmentDirections
                        .actionGlobalBookDetail(
                            bookId = book.id,
                            source = EntrySource.WISHLIST
                        )
                    if (!isEditingProfile)
                        findNavController().navigate(dir)
                }
            )
        )
    }

    private val bookTileAdapter by lazy {
        BookAdapter(
            mode = BookListMode.TILE,
            clicks = BookClicks(
                onClickItem = { book ->
                    val dir = BookDetailFragmentDirections
                        .actionGlobalBookDetail(
                            bookId = book.id,
                            source = EntrySource.MYBOOKSHELF
                        )
                    findNavController().navigate(dir)
                }
            )
        )
    }

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
        setupLocationDropdowns()
        observeViewModel()

    }

    private fun setupClickListeners() {
        binding.btnAddLocation.setOnClickListener { onClickAddLocation() }
    }

    private fun render() = with(binding) {
        rvReviews.visibility = if (currentTab == Tab.REVIEWS && !isReviewEmpty) View.VISIBLE else View.GONE
        tvReviewEmpty.visibility = if (currentTab == Tab.REVIEWS &&  isReviewEmpty) View.VISIBLE else View.GONE

        rvBooks.visibility = if (currentTab == Tab.BOOKS   && !isBookEmpty)   View.VISIBLE else View.GONE
        tvBookEmpty.visibility = if (currentTab == Tab.BOOKS   &&  isBookEmpty)   View.VISIBLE else View.GONE

        profileContainer.visibility = if (currentTab == Tab.PROFILE) View.VISIBLE else View.GONE

        val tabIndex = when (currentTab) {
            Tab.REVIEWS -> 0
            Tab.BOOKS   -> 1
            Tab.PROFILE -> 2
        }

        profileContainer.visibility = if (currentTab == Tab.PROFILE) View.VISIBLE else View.GONE

        if (currentTab == Tab.PROFILE) {
            rvWishlist.visibility = if (!isWishlistEmpty) View.VISIBLE else View.GONE
            tvWishlistEmpty.visibility = if (isWishlistEmpty)  View.VISIBLE else View.GONE
            btnAddWishlist.visibility = View.GONE
            tvGenreNone.visibility = if (!isEditingProfile && isGenreEmpty) View.VISIBLE else View.GONE
        } else {
            rvWishlist.visibility = View.GONE
            tvWishlistEmpty.visibility = View.GONE
            btnAddWishlist.visibility = View.GONE
        }
        updateFabForTab(tabIndex, isEditingProfile)
    }

    private fun observeViewModel() {
        viewModel.myReviews.observe(viewLifecycleOwner) { reviews ->
            reviewAdapter.submitList(reviews)
            isReviewEmpty = reviews.isEmpty()
            render()
        }

        viewModel.myBooks.observe(viewLifecycleOwner) { books ->
            bookTileAdapter.submitList(books)
            isBookEmpty = books.isEmpty()
            render()
        }

        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            if (profile == null) return@observe

            val fieldPlaceholder = getString(R.string.profile_field_empty)
            val bioPlaceholder = getString(R.string.profile_bio_empty)

            binding.tvName.text = profile.username
            binding.tvBio.text = profile.preferences.readingHabit.takeIf { !it.isNullOrEmpty() } ?: bioPlaceholder
            binding.ivProfileImage.loadAvatar(profile.profileUrl)
            binding.tvReviewCount.text = profile.reviewCount.toString()
            binding.tvFollowerCount.text = profile.followerCount.toString()
            binding.tvFollowingCount.text = profile.followingCount.toString()

            binding.tvTradeLocation1.text = profile.preferences.tradeLocation1
            binding.tvTradeLocation2.visibility = View.GONE
            binding.tvTradeSpot1.text = profile.preferences.tradeSpot1
            binding.tvReadingHabit.text = profile.preferences.readingHabit
            isGenreEmpty = profile.favoriteGenres.isEmpty()

            val favBook      = profile.preferences.favBooks?.firstOrNull()
            val favBookNote  = profile.preferences.favBookNotes?.firstOrNull()
            val favAuthor    = profile.preferences.favAuthors?.firstOrNull()
            val favAuthorNote= profile.preferences.favAuthorNotes?.firstOrNull()

            binding.tvFavBook.setTextOrGone(favBook)
            binding.tvFavBookNote.setTextOrGone(favBookNote)
            binding.tvFavAuthor.setTextOrGone(favAuthor)
            binding.tvFavAuthorNote.setTextOrGone(favAuthorNote)

            renderSelectedGenresFromViewModel(profile.favoriteGenres)
            syncEditChipsFromViewModel(profile.favoriteGenres)
            if (!isEditingProfile) {
                syncChipsFromProfile(profile)
            }
            render()
        }

        viewModel.myWishlist.observe(viewLifecycleOwner) { books ->
            bookRowAdapter.submitList(books)
            isWishlistEmpty = books.isEmpty()
            render()
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
        isEditingProfile = false
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
                val newTab = when (tab?.position) {
                    0 -> Tab.REVIEWS
                    1 -> Tab.BOOKS
                    else -> Tab.PROFILE
                }

                val newIndex = tab?.position ?: 0

                if (currentTab == Tab.PROFILE &&
                    newTab != Tab.PROFILE &&
                    isEditingProfile
                ) {
//                    showLeaveProfileEditDialog(newIndex)
                    handleLeaveFromLibrary(
                        onLeave = {
                            val newTab = when (newIndex) {
                                0 -> Tab.REVIEWS
                                1 -> Tab.BOOKS
                                else -> Tab.PROFILE
                            }
                            currentTab = newTab

                            binding.contentTabs.getTabAt(newIndex)?.select()
                            render()
                        },
                        onCancelled = {
                            binding.contentTabs.getTabAt(2)?.select()
                        }
                    )
                    return
                }

                currentTab = newTab
                render()
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {
            }

            override fun onTabReselected(tab: TabLayout.Tab?) {
            }
        })
        val index = when (currentTab) {
            Tab.REVIEWS -> 0
            Tab.BOOKS -> 1
            Tab.PROFILE -> 2
        }
        binding.contentTabs.getTabAt(index)?.select()
        render()
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
                    val action = LibraryFragmentDirections
                        .actionLibraryFragmentToAddBookFragment()
                    findNavController().navigate(action)
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

                        val location1 = selectedLocations.getOrNull(0)?.let { (city, district) -> "$city $district" }.orEmpty()
                        val location2 = selectedLocations.getOrNull(1)?.let { (city, district) -> "$city $district" }.orEmpty()

                        val newPrefs = currentProfile.preferences.copy(
                            tradeLocation1 = location1,
                            tradeLocation2 = location2,
                            tradeSpot1 = binding.editTradeSpot1.text.toString(),
                            favBooks = prependAndShift(
                                newValue = binding.editFavBook.text.toString(),
                                oldList = currentProfile.preferences.favBooks
                            ),
                            favBookNotes = prependAndShift(
                                newValue = binding.editFavBookNote.text.toString(),
                                oldList = currentProfile.preferences.favBookNotes
                            ),
                            favAuthors = prependAndShift(
                                newValue = binding.editFavAuthor.text.toString(),
                                oldList = currentProfile.preferences.favAuthors
                            ),
                            favAuthorNotes = prependAndShift(
                                newValue = binding.editFavAuthorNote.text.toString(),
                                oldList = currentProfile.preferences.favAuthorNotes
                            ),
                            readingHabit = binding.editReadingHabit.text.toString(),
                        )

                        val newProfile = currentProfile.copy(
                            preferences = newPrefs,
                            favoriteGenres = selectedGenres
                        )

                        viewModel.saveProfile(newProfile)
                        toggleProfileEdit()
                    }
                } else {
                    setImageResource(R.drawable.edit_icon)  // 편집
                    contentDescription = getString(R.string.fab_edit_profile)
                    setOnClickListener {
                        toggleProfileEdit()
                    }
                }
                show()
            }
        }
    }

    private fun toggleProfileEdit(): Unit = with(binding){
        val edit = isEditingProfile.not()
        isEditingProfile = edit

        TransitionManager.beginDelayedTransition(profileRoot as ViewGroup, AutoTransition())

        // 1) 보기/편집 뷰 묶음 전환 -------------------------------

        setGroupVisible(
            edit = edit,
            viewViews = listOf(tvTradeLocation1, tvTradeLocation2, tvTradeSpot1),
            editViews = listOf(locationEditorRow, menuTradeCity, menuTradeDistrict, chipGroupLocations, btnAddLocation, editTradeSpot1)
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

        btnAddWishlist.visibility = if (edit) View.VISIBLE else View.GONE

        // 2) 값 동기화

        if (edit) {
            // 보기 → 편집 (진입 시)
            val profile = viewModel.userProfile.value ?: return
            tvGenreNone.visibility = if (profile.favoriteGenres.isEmpty()) View.VISIBLE else View.GONE
            syncChipsFromProfile(profile)
            editTradeSpot1.setText(profile.preferences.tradeSpot1)
            editFavBook.setText(profile.preferences.favBooks?.firstOrNull().orEmpty())
            editFavBookNote.setText(profile.preferences.favBookNotes?.firstOrNull().orEmpty())
            editFavAuthor.setText(profile.preferences.favAuthors?.firstOrNull().orEmpty())
            editFavAuthorNote.setText(profile.preferences.favAuthorNotes?.firstOrNull().orEmpty())
            editReadingHabit.setText(profile.preferences.readingHabit)
            syncEditChipsFromViewModel(profile.favoriteGenres)

            autoCompleteLocation1.setText("", false)
            autoCompleteLocation2.setText("", false)
            autoCompleteLocation1.requestFocus()
        } else {
            hideKeyboard()
        }

        // 3) FAB 상태 갱신
        updateFabForTab(2, isEditingProfile)
        render()
    }

    private fun setupLocationDropdowns() = with(binding) {
        val json = requireContext().assets.open("locations.json").bufferedReader().use { it.readText() }
        val cities = org.json.JSONArray(json)

        val cityNames = ArrayList<String>(cities.length())
        val districtMap = HashMap<String, List<String>>(cities.length())

        for (i in 0 until cities.length()) {
            val obj = cities.getJSONObject(i)
            val name = obj.getString("name")
            cityNames.add(name)

            val arr = obj.getJSONArray("districts")
            val districts = ArrayList<String>(arr.length())
            for (j in 0 until arr.length()) districts.add(arr.getString(j))
            districtMap[name] = districts
        }

        val cityAdapter = android.widget.ArrayAdapter(requireContext(), android.R.layout.simple_list_item_1, cityNames)
        autoCompleteLocation1.setAdapter(cityAdapter)

        autoCompleteLocation1.setOnItemClickListener { _, _, position, _ ->
            val selCity = cityNames[position]
            val districts = districtMap[selCity] ?: emptyList()
            val districtAdapter = android.widget.ArrayAdapter(requireContext(), android.R.layout.simple_list_item_1, districts)
            autoCompleteLocation2.setAdapter(districtAdapter)
            autoCompleteLocation2.setText("", false) // 이전 선택 초기화
        }
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

    private fun refreshLocationLimitUi() = with(binding) {
        val canAdd = selectedLocations.size < 2

        btnAddLocation.isEnabled = canAdd
        menuTradeCity.isEnabled = canAdd
        menuTradeDistrict.isEnabled = canAdd
        autoCompleteLocation1.isEnabled = canAdd
        autoCompleteLocation2.isEnabled = canAdd

        if (!canAdd) {
            autoCompleteLocation1.setText("", false)
            autoCompleteLocation2.setText("", false)
        }
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

    private fun addChip(label: String, pair: Pair<String, String>) {
        val chip = com.google.android.material.chip.Chip(requireContext()).apply {
            text = label
            isCloseIconVisible = true
            setOnCloseIconClickListener {
                selectedLocations.remove(pair)
                binding.chipGroupLocations.removeView(this)
            }
        }
        binding.chipGroupLocations.addView(chip)
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

    private fun syncChipsFromProfile(profile: UserProfile) = with(binding) {
        chipGroupLocations.removeAllViews()
        selectedLocations.clear()

        val candidates = listOf(
            profile.preferences.tradeLocation1,
            profile.preferences.tradeLocation2
        ).filter { !it.isNullOrBlank() }

        candidates.forEach { s ->
            val parts = s!!.trim().split(Regex("\\s+"), limit = 2)
            if (parts.size == 2) {
                val pair = parts[0] to parts[1]
                selectedLocations += pair
                addChip(s, pair)
            }
        }
    }

    private fun onClickAddLocation() = with(binding) {
        val city = autoCompleteLocation1.text?.toString()?.trim().orEmpty()
        val district = autoCompleteLocation2.text?.toString()?.trim().orEmpty()

        if (selectedLocations.size >= 1) {
            Snackbar.make(requireView(), "선택한 지역을 취소하고 추가해주세요.", Snackbar.LENGTH_SHORT).show()
            return@with
        }

        if (city.isEmpty() || district.isEmpty()) {
            Snackbar.make(requireView(), "시/도와 시/군/구를 모두 선택하세요.", Snackbar.LENGTH_SHORT).show()
            return@with
        }

        val pair = city to district
        if (selectedLocations.any { it.first == city && it.second == district }) {
            Snackbar.make(requireView(), "이미 추가된 지역입니다.", Snackbar.LENGTH_SHORT).show()
            return@with
        }

        selectedLocations += pair
        addChip("$city $district", pair)

        autoCompleteLocation1.setText("", false)
        autoCompleteLocation2.setText("", false)
    }

    private fun prependAndShift(
        newValue: String,
        oldList: List<String>?,
        maxSize: Int = 10
    ): List<String>? {
        val trimmed = newValue.trim()
        if (trimmed.isEmpty())
            return emptyList()

        val result = mutableListOf<String>()
        result.add(trimmed)
        result.addAll(oldList ?: emptyList())
        return result.take(maxSize)
    }

    private fun TextView.setTextOrGone(value: String?) {
        if (value.isNullOrBlank()) {
            visibility = View.GONE
            text = ""
        } else {
            visibility = View.VISIBLE
            text = value
        }
    }

    private fun navigateToEditReview(review: Review) {
        val bundle = Bundle().apply {
            putBoolean("isEdit", true)
            putInt("reviewId", review.id)

            putString("bookTitle", review.bookTitle)
            putString("authorName", review.authorName)
            putString("content", review.content)
            putStringArrayList("imageUrls", ArrayList(review.imageUrls))
            putString("bookId", review.bookId)
        }

        findNavController().navigate(
            R.id.action_libraryFragment_to_writeReviewFragment,
            bundle
        )
    }

    private fun confirmDeleteReview(review: Review) {
        AlertDialog.Builder(requireContext())
            .setMessage("이 리뷰를 삭제할까요?")
            .setPositiveButton("삭제") { _, _ ->
                viewModel.deleteNewReview(review.id)
            }
            .setNegativeButton("취소", null)
            .show()
    }

    fun handleLeaveFromLibrary(
        onLeave: () -> Unit,
        onCancelled: () -> Unit = {}
    ) {
        if (!isEditingProfile) {
            onLeave()
            return
        }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("편집을 종료할까요?")
            .setMessage("작성 중인 프로필 변경 사항이 저장되지 않습니다.")
            .setPositiveButton("나가기") { _, _ ->
                if (isEditingProfile) {
                    toggleProfileEdit()
                    onLeave()
                }
            }
            .setNegativeButton("취소") { _, _ ->
                onCancelled()
            }
            .show()
    }

}
