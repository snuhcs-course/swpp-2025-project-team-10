package com.example.librarytogether.feature.onboarding

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.librarytogether.databinding.ItemChipSelectableBinding

class ChipSelectableAdapter(
    private val onToggle: (id: Int, isSelected: Boolean) -> Unit
) : ListAdapter<ChipSelectableAdapter.Item, ChipSelectableAdapter.VH>(ItemDiffCallback()) {

    data class Item(
        val id: Int,
        val label: String
    )
    private var selectedIds = emptySet<Int>()
    fun updateSelection(newSelectedIds: Set<Int>) {
        val oldSelection = this.selectedIds
        this.selectedIds = newSelectedIds

        (oldSelection + newSelectedIds).forEach { id ->
            val position = currentList.indexOfFirst { it.id == id }
            if (position != -1) {
                notifyItemChanged(position)
            }
        }
    }

    inner class VH(private val binding: ItemChipSelectableBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            binding.chip.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    val item = getItem(position)
                    onToggle(item.id, !selectedIds.contains(item.id))
                }
            }
        }

        fun bind(item: Item) {
            binding.chip.text = item.label
            binding.chip.isChecked = selectedIds.contains(item.id)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val inflater = LayoutInflater.from(parent.context)
        val binding = ItemChipSelectableBinding.inflate(inflater, parent, false)
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }
        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
