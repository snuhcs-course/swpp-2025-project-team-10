package com.example.librarytogether.feature.library
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.annotation.RequiresPermission
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.databinding.FragmentHomeBinding
import com.example.librarytogether.databinding.FragmentLibraryBinding
import com.example.librarytogether.feature.home.FeedAdapter
import com.example.librarytogether.feature.home.FeedClicks
import com.example.librarytogether.feature.home.data.HomeApi
import com.example.librarytogether.feature.library.LibraryViewModel
import com.example.librarytogether.network.RetrofitClient
import com.google.android.material.button.MaterialButtonToggleGroup
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.tabs.TabLayout
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LibraryFragment : Fragment() {

    private val viewModel: LibraryViewModel by viewModels()
    private var _binding: FragmentLibraryBinding? = null
    private val binding get() = _binding!!

    private val reviewAdapter by lazy { ReviewAdapter(
    ) }

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

    private fun setupRecyclerView() {
        binding.rvReviews.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = reviewAdapter
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
                        binding.fabAdd.show()
                    }
                    1 -> {
                        binding.rvReviews.visibility = View.GONE
                        binding.rvBooks.visibility = View.VISIBLE
                        binding.profileContainer.visibility = View.GONE
                        binding.fabAdd.show()
                    }
                    2 -> {
                        binding.rvReviews.visibility = View.GONE
                        binding.rvBooks.visibility = View.GONE
                        binding.profileContainer.visibility = View.VISIBLE
                        binding.fabAdd.hide()
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
        binding.fabAdd.show()
    }

    private fun setupClickListeners() {
        binding.fabAdd.setOnClickListener {
            when (binding.contentTabs.selectedTabPosition) {
                0 -> {
                    WriteReviewSheet().show(childFragmentManager, "WriteReviewSheet")
                }
                1 -> {
                }
                2 -> {
                }
            }
        }
    }

    private fun observeViewModel() {
        viewModel.myReviews.observe(viewLifecycleOwner) { reviews ->
            reviewAdapter.submitList(reviews)
//            binding.tvEmpty.isVisible = reviews.isEmpty()
//            binding.rvReviews.isVisible = reviews.isNotEmpty()
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
}