package com.example.librarytogether.feature.notification

import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.librarytogether.R
import com.example.librarytogether.databinding.FragmentNotificationBinding
import com.example.librarytogether.feature.notification.data.NotificationDto
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class NotificationFragment : Fragment(R.layout.fragment_notification) {

    private var _binding: FragmentNotificationBinding? = null
    private val binding get() = _binding!!

    private val vm: NotificationViewModel by viewModels()
    private lateinit var adapter: NotificationAdapter

    private var allNotifications: List<NotificationDto> = emptyList()
    private enum class FilterType { EXCHANGE, SOCIAL }
    private var currentFilter: FilterType = FilterType.EXCHANGE

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentNotificationBinding.bind(view)

        adapter = NotificationAdapter(
            NotificationClicks(
                onClickItem = { item ->
                    //vm.markAsRead(item)
                    item.deepLink?.let { link ->
                        runCatching {
                            startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, Uri.parse(link)))
                        }
                    }
                },
                onClickAction = { item ->
                    //vm.markAsRead(item)
                    Log.d("NotificationFragment", "onClickAction called. item = $item")

                    when (item.type){
                        "barter_request" -> {
                            val requestId = item.related_object_id
                            if (!requestId.isNullOrEmpty()) {
                                val action =
                                    NotificationFragmentDirections
                                        .actionNotificationToBarterApprovalFragment(requestId = requestId)
                                findNavController().navigate(action)
                            }
                        }
                        "barter_request_sent" -> {
                            vm.cancelBarter(item)
                        }
                        else -> {
                        }
                    }
                }
            )
        )

        binding.rvNotifications.layoutManager = LinearLayoutManager(requireContext())
        binding.rvNotifications.adapter = adapter

        setupFilterChips()

        binding.swipeRefresh.setOnRefreshListener { vm.load() }

        vm.items.observe(viewLifecycleOwner) { list ->
            allNotifications = list
            val closedIds = list
                .filter { it.type == "barter_completed" || it.type == "barter_accepted" || it.type == "barter_rejected" }
                .mapNotNull { it.related_object_id }
                .toSet()
            adapter.updateClosedBarterIds(closedIds)
            applyFilter()
            binding.emptyView.visibility = if (list.isEmpty()) View.VISIBLE else View.GONE
        }

        vm.loading.observe(viewLifecycleOwner) {
            binding.progress.visibility = if (it) View.VISIBLE else View.GONE
            binding.swipeRefresh.isRefreshing = false
        }

        vm.snackbarMessage.observe(viewLifecycleOwner) { msg ->
            if (!msg.isNullOrEmpty()) {
                com.google.android.material.snackbar.Snackbar
                    .make(binding.root, msg, com.google.android.material.snackbar.Snackbar.LENGTH_SHORT)
                    .show()
                vm.onSnackbarShown()
            }
        }

        vm.load()
    }


    private fun setupFilterChips() {
        binding.chipExchange.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                currentFilter = FilterType.EXCHANGE
                applyFilter()
            }
        }
        binding.chipSocial.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                currentFilter = FilterType.SOCIAL
                applyFilter()
            }
        }
    }

    private fun applyFilter() {
        val filtered = when (currentFilter) {
            FilterType.EXCHANGE -> {
                allNotifications.filter { it.type.startsWith("barter_") }
            }
            FilterType.SOCIAL -> {
                allNotifications.filter { !it.type.startsWith("barter_") }
            }
        }

        adapter.submitList(filtered)
        binding.emptyView.visibility =
            if (filtered.isEmpty()) View.VISIBLE else View.GONE
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
